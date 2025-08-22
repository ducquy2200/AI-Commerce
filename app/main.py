import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime
import base64
from app.config import get_settings
from app.middleware import log_requests, rate_limit_middleware, error_handler
from app.monitoring import metrics
from app.tools import create_tools, current_image_store
from app.utils import clean_agent_response
from app.models import Product, MessageType
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from typing import Dict
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Commerce Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(log_requests)
app.middleware("http")(rate_limit_middleware)
app.add_exception_handler(Exception, error_handler)

class AICommerceAgent:
    def __init__(self):
        # Get settings from config
        settings = get_settings()
        
        # Validate API key
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key  # Use from config
        )
        
        # Initialize memory for conversation
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10,  # Keep last 10 messages
            output_key="output"  # Specify which output key to use
        )
            
        # Get tools from tools.py
        self.tools = create_tools()
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are CommerceAI, an AI shopping assistant for an e-commerce website. 
            You help customers find products, answer questions, and provide recommendations.
            You have access to a product catalog and can search for items based on text descriptions or images.
            
            When calling search_by_image, pass a descriptive query about what to search for, like:
            - "similar shirts" if looking for shirts
            - "matching style" for style-based search
            - "same color items" for color matching
            - Don't just pass "uploaded_image" or generic text
            
            Be friendly, helpful, and concise in your responses."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=False
        )
    
    def process_message(self, message: str, image: Optional[str] = None, session_id: str = None) -> Dict:
        """Process a message and return response with products if applicable"""
        
        # Handle image uploads
        input_message = message
        if image:
            current_image_store["image"] = image
            input_message = f"[User uploaded an image] {message}"
        else:
            current_image_store["image"] = None
        
        try:
            # Run agent
            result = self.agent_executor.invoke({"input": input_message})
            
            # Get the response
            raw_response = result.get("output", "I'm sorry, I couldn't process your request.")
            
            # Initialize default values
            products = None
            message_type = "text"
            
            # Check if the response mentions products
            if any(keyword in raw_response.lower() for keyword in ['found', 'products', 'here are', 'similar']):
                # Determine search type
                if image:
                    message_type = "image_search"
                else:
                    message_type = "product_recommendation"
                
                # Extract products based on the last tool used
                try:
                    from app.tools import vector_store
                    
                    if image and "similar" in raw_response.lower():
                        # Image search
                        embedding = vector_store.image_processor.get_image_embedding(image)
                        product_results = vector_store.search_by_image_embedding(embedding, n_results=5)
                    else:
                        # Text search - extract query from message
                        search_query = message
                        product_results = vector_store.search_products(search_query, n_results=5)
                    
                    # Convert to Product models
                    if product_results:
                        products = []
                        for p in product_results:
                            try:
                                product_dict = {
                                    'id': p.get('id', 'unknown'),
                                    'name': p.get('name', 'Unknown Product'),
                                    'description': p.get('description', ''),
                                    'price': float(p.get('price', 0)),
                                    'category': p.get('category', 'General'),
                                    'sub_category': p.get('sub_category'),
                                    'brand': p.get('brand'),
                                    'color': p.get('color'),
                                    'gender': p.get('gender'),
                                    'in_stock': p.get('in_stock', True),
                                    'image_base64': p.get('image_base64'),  # Include base64 image
                                    'similarity_score': p.get('similarity_score')
                                }
                                
                                product = Product(**product_dict)
                                products.append(product.model_dump())  # Convert to dict
                            except Exception as e:
                                logger.error(f"Error creating product model: {e}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error extracting products: {e}")
            
            return {
                "response": raw_response,
                "products": products,
                "session_id": session_id,
                "message_type": message_type
            }
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "products": None,
                "session_id": session_id,
                "message_type": "text"
            }
    
commerce_agent = AICommerceAgent()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    image: Optional[str] = None  # Base64 encoded image
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    products: Optional[List[Dict[str, Any]]] = None
    session_id: str
    timestamp: datetime
    message_type: str = "text"  # text, product_recommendation, image_search

class WebSocketMessage(BaseModel):
    type: str  # "chat", "typing", "error"
    data: Dict[str, Any]

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "AI Commerce Agent API is running"}

@app.get("/metrics")
async def get_metrics():
    """
    Get API metrics
    """
    return metrics.get_metrics()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

# REST endpoint for chat
@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Main chat endpoint that handles both text and image inputs
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Check if agent is initialized
        if not commerce_agent:
            return ChatResponse(
                response="I'm currently unavailable. Please try again later.",
                products=None,
                session_id=session_id,
                timestamp=datetime.now(),
                message_type=MessageType.ERROR
            )
        
        # Process with LangChain agent
        agent_response = commerce_agent.process_message(
            message=chat_message.message,
            image=chat_message.image,
            session_id=session_id
        )
        
        # Ensure message_type is valid enum value
        message_type_str = agent_response.get("message_type", "text")
        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            # Default to text if invalid
            message_type = MessageType.TEXT
        
        # Convert Product objects to dicts if they exist
        products = agent_response.get("products")
        if products and isinstance(products, list) and len(products) > 0:
            # Check if first item is a Product object
            if hasattr(products[0], 'model_dump'):
                products = [p.model_dump() for p in products]
            elif hasattr(products[0], 'dict'):
                products = [p.dict() for p in products]
        
        return ChatResponse(
            response=agent_response["response"],
            products=products,
            session_id=session_id,
            timestamp=datetime.now(),
            message_type=message_type
        )
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        traceback.print_exc()
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            products=None,
            session_id=session_id,
            timestamp=datetime.now(),
            message_type=MessageType.ERROR
        )

# File upload endpoint for images
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to upload images for product search
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Read file and convert to base64
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode()
        
        return {
            "status": "success",
            "image_data": base64_image,
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat communication
    """
    await manager.connect(websocket, client_id)
    metrics.record_websocket_connection(connected=True)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create WebSocket message
            ws_message = WebSocketMessage(
                type=message_data.get("type", "chat"),
                data=message_data.get("data", {})
            )
            
            # Handle different message types
            if ws_message.type == "chat":
                # Process with LangChain agent
                agent_response = commerce_agent.process_message(
                    message=ws_message.data.get('message', ''),
                    image=ws_message.data.get('image'),
                    session_id=client_id
                )
                
                response = {
                    "type": "response",
                    "data": {
                        "message": agent_response["response"],
                        "products": agent_response.get("products"),
                        "timestamp": datetime.now().isoformat(),
                        "session_id": client_id
                    }
                }
                
                await manager.send_message(json.dumps(response), client_id)
                
            elif ws_message.type == "typing":
                # Broadcast typing indicator to other clients if needed
                pass
                
            elif ws_message.type == "ping":
                # Handle ping for connection keep-alive
                pong_response = {"type": "pong", "data": {"timestamp": datetime.now().isoformat()}}
                await manager.send_message(json.dumps(pong_response), client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        metrics.record_websocket_connection(connected=False)
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")
        manager.disconnect(client_id)
        metrics.record_websocket_connection(connected=False)

# Session management endpoints
@app.post("/session/create")
async def create_session():
    """
    Create a new chat session
    """
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "created_at": datetime.now(),
        "status": "active"
    }

@app.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get chat history for a session
    """
    # TODO: Implement session history retrieval from database
    return {
        "session_id": session_id,
        "messages": [],
        "status": "not_implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)