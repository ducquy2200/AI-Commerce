from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "AI Commerce Agent"
    version: str = "1.0.0"
    debug: bool = True
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # File Upload Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: list = ["image/jpeg", "image/png", "image/jpg"]
    
    # WebSocket Settings
    ws_heartbeat_interval: int = 30  # seconds

    # OpenAI Configuration - loaded from environment
    openai_api_key: Optional[str] = None
    
     # Model Configuration
    embedding_model: str = "text-embedding-ada-002"
    llm_model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Vector Database
    chroma_persist_directory: str = "./chroma_db"
    
    # API Gateway URL (for callbacks)
    api_gateway_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()