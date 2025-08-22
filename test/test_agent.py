import asyncio
import httpx
import json
from datetime import datetime

async def test_agent_integration():
    """Test the agent integration with various queries"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "General Chat",
            "message": "What's your name and what can you do?"
        },
        {
            "name": "Product Search",
            "message": "I need a sports t-shirt for running"
        },
        {
            "name": "Specific Search",
            "message": "Show me Nike products"
        },
        {
            "name": "Category Browse",
            "message": "What electronics do you have?"
        },
        {
            "name": "Price Query",
            "message": "Find me something under $50"
        }
    ]
    
    # Create client with longer timeout
    timeout = httpx.Timeout(30.0, connect=5.0)  # 30 seconds for read, 5 for connect
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        print("Testing LangChain Agent Integration\n" + "="*50)
        
        for test in test_cases:
            print(f"\n📝 Test: {test['name']}")
            print(f"Message: {test['message']}")
            
            try:
                start_time = datetime.now()
                response = await client.post(
                    f"{base_url}/chat",
                    json={"message": test['message']}
                )
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Response: {data['response'][:200]}...")  # Show first 200 chars
                    print(f"⏱️  Response time: {response_time:.2f}s")
                    
                    if data.get('products'):
                        print(f"📦 Products found: {len(data['products'])}")
                        for product in data['products'][:3]:  # Show first 3 products
                            print(f"   - {product['name']} (${product['price']})")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"Response: {response.text}")
                    
            except httpx.TimeoutException:
                print(f"⏱️  Timeout: Request took too long (>30s)")
                print("💡 Tip: First requests may be slow as models load")
            except Exception as e:
                print(f"❌ Error: {type(e).__name__}: {str(e)}")
            
            await asyncio.sleep(1)  # Small delay between requests

if __name__ == "__main__":
    print("🚀 Starting tests... (this may take a moment)\n")
    asyncio.run(test_agent_integration())