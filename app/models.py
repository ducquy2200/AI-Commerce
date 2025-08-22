from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    IMAGE_SEARCH = "image_search"
    ERROR = "error"

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: Optional[str] = "General"
    sub_category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None  # Add this field
    in_stock: bool = True
    features: Optional[List[str]] = []
    attributes: Optional[Dict[str, Any]] = {}
    similarity_score: Optional[float] = None
    
    class Config:
        extra = "allow"  # Allow extra fields

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    image: Optional[str] = Field(None, description="Base64 encoded image")
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    response: str
    products: Optional[List[Product]] = None
    session_id: str
    timestamp: datetime
    message_type: MessageType
    confidence_score: Optional[float] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class WebSocketMessage(BaseModel):
    type: Literal["chat", "typing", "ping", "pong", "error"]
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)