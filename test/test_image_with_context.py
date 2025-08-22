# test_image_with_context.py
import requests
import base64
from PIL import Image
import io

def test_with_different_contexts():
    """Test image search with different query contexts"""
    
    # Create a test image
    img = Image.new('RGB', (200, 200), color='blue')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Test different messages
    test_cases = [
        "Find similar products to this image",
        "I want a shirt like this",
        "Show me similar blue items",
        "Find products with this style",
        "I need something like this but in red"
    ]
    
    print("🧪 Testing Image Search with Different Contexts\n" + "="*50)
    
    for message in test_cases:
        print(f"\n📝 Testing: '{message}'")
        
        response = requests.post(
            "http://localhost:8000/chat",
            json={
                "message": message,
                "image": img_base64
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response preview: {data['response'][:150]}...")
            print(f"   Message type: {data.get('message_type')}")
            print(f"   Products found: {len(data.get('products', []))}")
        else:
            print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    test_with_different_contexts()