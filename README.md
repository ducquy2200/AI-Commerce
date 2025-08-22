# AI Commerce Assistant - Backend Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Design Decisions](#design-decisions)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Data Models](#data-models)

## Overview

The AI Commerce Assistant backend is a FastAPI-based service that provides an intelligent shopping assistant powered by LangChain and OpenAI's GPT-4. It offers natural language product search, image-based similarity search, and conversational commerce capabilities.

### Key Features
- 🤖 **AI-Powered Chat**: Natural language understanding using GPT-4
- 🔍 **Semantic Search**: Vector-based product search using ChromaDB
- 📸 **Image Search**: CLIP-based image similarity matching
- 🔄 **Real-time Communication**: WebSocket support for live chat
- 📦 **Product Catalog**: Integration with HuggingFace fashion dataset
- 🚀 **Production Ready**: Docker support, error handling, and monitoring

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                              │
│                       (Web App / Mobile / API)                      │
└─────────────────────────┬───────────────┬───────────────────────────┘
                          │   HTTP/WS     │
                          ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API Gateway                                │
│                    (FastAPI + WebSocket)                            │
│          • REST Endpoints      • WebSocket Handler                  │
│          • CORS Middleware     • Request Validation                 │
│          • Error Handling      • Rate Limiting                      │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LangChain Agent Orchestrator                     │
│          • Intent Recognition  • Tool Selection                     │
│          • Context Management  • Response Generation                │
└───────────────────────┬──────────────┬──────────────┬───────────────┘
                        │              │              │
                        ▼              ▼              ▼
                ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
                │   General   │ │   Product   │ │    Image    │
                │ Chat Tool   │ │ Search Tool │ │ Search Tool │
                └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
                       │               │               │
                       ▼               ▼               ▼
          ┌─────────────┐ ┌─────────────────────────┐ ┌─────────────────┐
          │  GPT-4 LLM  │ │    Vector Database      │ │ Image Processor │
          │             │ │     (ChromaDB)          │ │     (CLIP)      │
          └─────────────┘ └───────────┬─────────────┘ └────────┬────────┘
                                      │                        │
                                      ▼                        ▼
                            ┌─────────────────────────────────────────┐
                            │        Fashion Dataset (HuggingFace)    │
                            │         44,000+ Products with Images    │
                            └─────────────────────────────────────────┘
```

### Component Details

#### 1. **API Gateway (FastAPI)**
- Handles HTTP requests and WebSocket connections
- Provides request validation using Pydantic models
- Implements CORS for cross-origin requests
- Includes middleware for logging, monitoring, and rate limiting

#### 2. **LangChain Agent Orchestrator**
- Uses ReAct pattern for reasoning and action selection
- Maintains conversation context with memory management
- Selects appropriate tools based on user intent
- Generates natural language responses

#### 3. **Tool Suite**
- **General Chat**: Direct LLM responses for conversational queries
- **Product Search**: Semantic search using text embeddings
- **Image Search**: Visual similarity using CLIP embeddings

#### 4. **Vector Database (ChromaDB)**
- Stores product embeddings for semantic search
- Separate collections for text and image embeddings
- Persistent storage with efficient similarity search

#### 5. **Data Layer**
- HuggingFace fashion dataset integration
- 44,000+ real fashion products with images
- Dynamic price generation and inventory management

## Design Decisions

### 1. **Why FastAPI?**
- **Performance**: Built on Starlette and Pydantic for high performance
- **Developer Experience**: Automatic API documentation (Swagger/OpenAPI)
- **Type Safety**: Full Python type hints support
- **Async Support**: Native async/await for concurrent operations
- **WebSocket Support**: Built-in WebSocket handling

### 2. **Why LangChain?**
- **Flexibility**: Easy to swap LLMs or add new tools
- **Agent Framework**: Built-in ReAct agent for complex reasoning
- **Memory Management**: Conversation history handling
- **Tool Integration**: Simple interface for adding capabilities

### 3. **Why ChromaDB?**
- **Simplicity**: Embedded database, no separate service needed
- **Performance**: Fast similarity search
- **Persistence**: Local storage for embeddings
- **Open Source**: Active community and development

### 4. **Why CLIP for Image Search?**
- **Multimodal**: Understands both text and images
- **Pre-trained**: No need for custom training
- **Quality**: State-of-the-art image understanding
- **Efficiency**: Reasonable model size for deployment

### 5. **Architecture Patterns**
- **Singleton Pattern**: For dataset loader to prevent multiple loads
- **Factory Pattern**: For creating tools and configurations
- **Repository Pattern**: Vector store abstracts data access
- **Middleware Pattern**: For cross-cutting concerns

## Tech Stack

### Core Technologies
- **Python 3.13+**: Modern Python with type hints
- **FastAPI**: Web framework
- **LangChain**: LLM orchestration
- **OpenAI GPT-4**: Language model
- **ChromaDB**: Vector database
- **Sentence Transformers**: CLIP for image embeddings

## Project Structure

```
ai-commerce-assistant/
├── app/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── fashion_dataset.py   # HuggingFace dataset loader
│   ├── image_cache.py       # Image caching functionality
│   ├── image_processor.py   # CLIP image processing
│   ├── main.py              # FastAPI application & endpoints
│   ├── middleware.py        # Custom middleware
│   ├── models.py            # Pydantic models for request/response
│   ├── monitoring_agent.py  # Agent-specific monitoring
│   ├── monitoring.py        # General metrics and monitoring
│   ├── tools.py             # LangChain tools for agent
│   ├── utils.py             # Utility functions
│   └── vector_store.py      # ChromaDB integration
├── test/                    # Test files
│   ├── debug_test.py
│   ├── test_agent.py
│   ├── test_api.py
│   ├── test_client.py
│   ├── test_enhanced_image_search.py
│   ├── test_image_complete.py
│   ├── test_image_search.py
│   ├── test_image_similarity.html
│   ├── test_image_upload.html
│   ├── test_image_with_context.py
│   └── test_websocket.html
├── .dockerignore           # Docker ignore patterns
├── .env                    # Environment variables
├── .env.production         # Production environment variables
├── .gitignore              # Git ignore patterns
├── check_config.py         # Configuration validation script
├── docker-compose.prod.yml # Production Docker compose
├── docker-compose.yml      # Main Docker compose
├── docker-entrypoint.sh    # Docker entry script
├── Dockerfile              # Main Dockerfile
├── Dockerfile.production   # Production Dockerfile
├── image_cache.json        # Image cache data
├── init_agent.py           # Agent initialization script
├── init_fashion_dataset.py # Dataset initialization script
├── ngrok.yml               # Ngrok configuration
├── README.md               # Project documentation
├── render.yaml             # Render deployment config
├── requirements.txt        # Python dependencies
├── run_with_agent.sh       # Run script with agent
├── run.py                  # Application entry point
└── start.sh                # Start script
```

## Docker Commands

### Prerequisites
Ensure Docker and Docker Compose are installed on your system.

### Running with Docker

#### 1. **Development Mode** (with hot reload)
```bash
# Run both backend and frontend with hot reload
docker-compose -f docker-compose.dev.yml up

# Run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```
Available at: http://localhost:8000

#### 2. **Production Mode**
```bash
# Build and run production containers
docker-compose up --build

# Run in background
docker-compose up -d

# Run with specific environment file
docker-compose --env-file .env.production up
```
Available at: http://localhost:8000

# API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: Configure based on deployment

## REST Endpoints

#### `GET /`
Returns API status message.

**Response:**
```json
{
  "message": "AI Commerce Agent API is running"
}
```

#### `GET /health`
Returns health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0"
}
```

#### `GET /metrics`
Returns API usage metrics.

**Response:**
```json
{
  "requests_total": 1500,
  "requests_per_minute": 25,
  "average_response_time": 0.150,
  "active_websocket_connections": 5
}
```

### Core Endpoints

#### `POST /chat`
Main chat endpoint for text and image-based queries.

**Request Body:**
```json
{
  "message": "string",
  "image": "string",        // Optional: Base64 encoded
  "session_id": "string"    // Optional
}
```

**Response:**
```json
{
  "response": "string",
  "products": [Product],    // Optional
  "session_id": "string",
  "timestamp": "datetime",
  "message_type": "string"  // text|product_recommendation|image_search|error
}
```

#### `POST /upload/image`
Upload image file for product search.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (JPEG/PNG/JPG)

**Response:**
```json
{
  "status": "success",
  "image_data": "string",   // Base64 encoded
  "filename": "string",
  "content_type": "string"
}
```

#### `POST /session/create`
Create new chat session.

**Response:**
```json
{
  "session_id": "string",
  "created_at": "datetime",
  "status": "active"
}
```

#### `GET /session/{session_id}/history`
Get chat history for session (not implemented).

**Response:**
```json
{
  "session_id": "string",
  "messages": [],
  "status": "not_implemented"
}
```

#### `WS /ws/{client_id}`
Real-time chat communication.

**Client Message:**
```json
{
  "type": "chat|typing|ping",
  "data": {
    "message": "string",
    "image": "string"     // Optional
  }
}
```

**Server Message:**
```json
{
  "type": "response|pong",
  "data": {
    "message": "string",
    "products": [Product],  // Optional
    "timestamp": "string",
    "session_id": "string"
  }
}
```

All endpoints are listed in http://localhost:8000/docs (OpenAPI-based)

## Data Models

### Product
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": 0.0,
  "category": "string",
  "sub_category": "string",
  "brand": "string",
  "color": "string",
  "gender": "string",
  "in_stock": true,
  "image_base64": "string",
  "similarity_score": 0.0
}
```

The mock data is pulled from https://huggingface.co/datasets/ashraq/fashion-product-images-small