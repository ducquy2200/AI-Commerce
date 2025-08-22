import base64
import requests
import json
from PIL import Image
import io
import numpy as np

class ImageSearchTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def create_test_images(self):
        """Create various test images"""
        images = {}
        
        # Red shirt-like image
        red_shirt = Image.new('RGB', (200, 200), color='red')
        draw = ImageDraw.Draw(red_shirt)
        draw.rectangle([50, 30, 150, 170], fill='darkred')
        images['red_shirt'] = self._image_to_base64(red_shirt)
        
        # Blue shirt-like image  
        blue_shirt = Image.new('RGB', (200, 200), color='lightblue')
        draw = ImageDraw.Draw(blue_shirt)
        draw.rectangle([50, 30, 150, 170], fill='blue')
        images['blue_shirt'] = self._image_to_base64(blue_shirt)
        
        # Shoe-like image
        shoe = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(shoe)
        draw.ellipse([20, 20, 180, 80], fill='black')
        images['shoe'] = self._image_to_base64(shoe)
        return images
    
    def _image_to_base64(self, image):
        """Convert PIL Image to base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def test_image_search_flow(self):
        """Test the complete image search flow"""
        print("🧪 Testing Complete Image Search Flow\n" + "="*50)
        
        # Create test images
        test_images = self.create_test_images()
        
        # Test each image
        for image_name, image_base64 in test_images.items():
            print(f"\n📸 Testing with {image_name}")
            
            payload = {
                "message": f"Find products similar to this {image_name.replace('_', ' ')}",
                "image": image_base64
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Response: {data['response'][:150]}...")
                    
                    if data.get('products'):
                        print(f"📦 Found {len(data['products'])} products")
                        for p in data['products'][:2]:
                            print(f"   - {p['name']} (${p['price']})")
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def test_websocket_image(self):
        """Test image search via WebSocket"""
        import websocket
        import json
        
        print("\n🔌 Testing WebSocket Image Search")
        
        # Create a simple test image
        test_image = self._image_to_base64(
            Image.new('RGB', (100, 100), color='red')
        )
        
        ws_url = "ws://localhost:8000/ws/test-image-client"
        
        def on_message(ws, message):
            data = json.loads(message)
            print(f"✅ WebSocket Response: {data}")
            ws.close()
        
        def on_open(ws):
            message = {
                "type": "chat",
                "data": {
                    "message": "Find similar products",
                    "image": test_image
                }
            }
            ws.send(json.dumps(message))
            print("📤 Sent image via WebSocket")
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message
        )
        
        ws.run_forever()

if __name__ == "__main__":
    from PIL import ImageDraw
    
    tester = ImageSearchTester()
    
    # Run all tests
    tester.test_image_search_flow()
    tester.test_websocket_image()