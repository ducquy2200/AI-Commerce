import base64
import requests
import os
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored rectangle as a test image
    img = Image.new('RGB', (100, 100), color='blue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Convert to base64
    return base64.b64encode(img_bytes.read()).decode('utf-8')

def encode_image_from_file(filepath):
    """Encode an image file to base64"""
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_image_search():
    base_url = "http://localhost:8000"
    
    print("🖼️  Testing Image-Based Product Search\n" + "="*50)
    
    # Test 1: Upload image endpoint
    print("\n📝 Test 1: Image Upload Endpoint")
    
    # Create a test image file
    test_img = Image.new('RGB', (200, 200), color='red')
    test_img.save('test_shirt.jpg')
    
    with open('test_shirt.jpg', 'rb') as f:
        files = {'file': ('test_shirt.jpg', f, 'image/jpeg')}
        response = requests.post(f"{base_url}/upload/image", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Image uploaded successfully")
        print(f"   Filename: {data.get('filename')}")
        base64_image = data.get('image_data')
    else:
        print(f"❌ Upload failed: {response.status_code}")
        base64_image = create_test_image()
    
    # Test 2: Chat with image
    print("\n📝 Test 2: Chat with Image Search")
    
    chat_payload = {
        "message": "Find products similar to this image",
        "image": base64_image
    }
    
    print("⏳ Sending image to chat endpoint...")
    response = requests.post(
        f"{base_url}/chat",
        json=chat_payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['response']}")
        print(f"   Message type: {data.get('message_type')}")
        
        if data.get('products'):
            print(f"\n📦 Found {len(data['products'])} similar products:")
            for product in data['products']:
                print(f"   - {product['name']} (${product['price']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Clean up
    os.remove('test_shirt.jpg')
    
    # Test 3: Test with different image descriptions
    print("\n📝 Test 3: Image + Text Description")
    
    chat_payload = {
        "message": "I want something similar to this but in blue color",
        "image": base64_image
    }
    
    response = requests.post(
        f"{base_url}/chat",
        json=chat_payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Response: {data['response'][:200]}...")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_image_search()