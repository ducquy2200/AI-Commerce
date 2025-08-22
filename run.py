import uvicorn
from app.main import app
from app.config import get_settings

settings = get_settings()

if not settings.openai_api_key:
    print("❌ Error: OPENAI_API_KEY not found in environment variables")
    print("Please add OPENAI_API_KEY to your .env file")
    exit(1)

if __name__ == "__main__":
    print(f"🚀 Starting {settings.app_name} v{settings.version}")
    print(f"📍 API running at http://{settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info"
    )