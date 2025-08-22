import requests
import json

def test_image_search_debug():
    """Test image search with detailed debugging"""
    
    # Create a simple test image (red square)
    from PIL import Image
    import base64
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    print("🧪 Testing Image Search with Debug Info\n" + "="*50)
    
    # Make request
    url = "http://localhost:8000/chat"
    payload = {
        "message": "Find similar products to this image",
        "image": img_base64
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success!")
            print(f"Response: {data['response'][:200]}...")
            print(f"Message Type: {data.get('message_type')}")
            print(f"Products: {len(data.get('products', []))} found")
            
            if data.get('products'):
                for p in data['products'][:2]:
                    print(f"\n- {p['name']}")
                    print(f"  ID: {p['id']}")
                    print(f"  Price: ${p['price']}")
                    print(f"  Category: {p.get('category', 'N/A')}")
        else:
            print(f"\n❌ Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    test_image_search_debug()