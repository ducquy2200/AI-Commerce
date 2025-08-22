"""
Script to validate configuration before running the app
"""
from app.config import get_settings
import sys

def check_config():
    try:
        settings = get_settings()
        
        print("🔍 Checking configuration...")
        
        # Check OpenAI API key
        if not settings.openai_api_key:
            print("❌ Error: OPENAI_API_KEY not found in .env file")
            return False
        
        # Mask the API key for security
        masked_key = settings.openai_api_key[:8] + "..." + settings.openai_api_key[-4:]
        print(f"✅ OpenAI API Key found: {masked_key}")
        
        # Check other important settings
        print(f"✅ Model: {settings.llm_model}")
        print(f"✅ Embedding Model: {settings.embedding_model}")
        print(f"✅ ChromaDB Directory: {settings.chroma_persist_directory}")
        print(f"✅ API Host: {settings.api_host}:{settings.api_port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    if not check_config():
        sys.exit(1)
    print("\n✅ Configuration is valid!")