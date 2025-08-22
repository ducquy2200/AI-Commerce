import base64
import requests
import json
from PIL import Image, ImageDraw
import io
import time

def create_product_like_images():
    """Create test images that look like products"""
    images = {}
    
    # Create a red t-shirt image
    red_shirt = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(red_shirt)
    # Body
    draw.polygon([(100, 80), (200, 80), (220, 200), (80, 200)], fill='red')
    # Sleeves
    draw.polygon([(100, 80), (80, 120), (60, 100), (80, 80)], fill='red')
    draw.polygon([(200, 80), (220, 80), (240, 100), (220, 120)], fill='red')
    # Collar
    draw.ellipse([(140, 70), (160, 90)], fill='white')
    
    # Create a blue jacket image
    blue_jacket = Image.new('RGB', (300, 300), color='white')
    draw = ImageDraw.Draw(blue_jacket)
    # Body
    draw.rectangle([(80, 80), (220, 250)], fill='navy')
    # Zipper line
    draw.line([(150, 80), (150, 250)], fill='silver', width=3)
    # Collar
    draw.polygon([(80, 80), (100, 60), (200, 60), (220, 80)], fill='darkblue')
    
    # Create shoe image
    shoe = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(shoe)
    # Shoe shape
    # Shoe shape
    draw.ellipse([(20, 80), (280, 160)], fill='gray')
    draw.ellipse([(200, 70), (270, 130)], fill='darkgray')
    # Laces
    for i in range(5):
        y = 90 + i * 10
        draw.line([(50 + i*20, y), (50 + i*20, y+5)], fill='white', width=2)
    
    # Convert to base64
    for name, img in [('red_shirt', red_shirt), ('blue_jacket', blue_jacket), ('shoe', shoe)]:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        images[name] = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return images

def test_enhanced_image_search():
    base_url = "http://localhost:8000"
    
    print("🖼️  Testing Enhanced Image-Based Product Search\n" + "="*50)
    
    # Create test images
    test_images = create_product_like_images()
    
    # Test each image
    test_cases = [
        {
            'name': 'Red T-Shirt Image',
            'image_key': 'red_shirt',
            'message': 'Find similar shirts'
        },
        {
            'name': 'Blue Jacket Image',
            'image_key': 'blue_jacket',
            'message': 'Show me jackets like this'
        },
        {
            'name': 'Shoe Image',
            'image_key': 'shoe',
            'message': 'Find similar footwear'
        }
    ]
    
    for test in test_cases:
        print(f"\n📸 Test: {test['name']}")
        print(f"Message: {test['message']}")
        
        payload = {
            "message": test['message'],
            "image": test_images[test['image_key']]
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json=payload,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received in {elapsed_time:.2f}s")
                print(f"Agent says: {data['response'][:200]}...")
                
                if data.get('products'):
                    print(f"\n📦 Found {len(data['products'])} products:")
                    for product in data['products'][:3]:
                        print(f"   - {product['name']} (${product['price']})")
                        if 'similarity_score' in product:
                            print(f"     Similarity: {product['similarity_score']*100:.1f}%")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test with combined text and image
    print("\n\n📸 Test: Image + Text Context")
    print("Message: I want something like this but in green color")
    
    payload = {
        "message": "I want something like this but in green color",
        "image": test_images['blue_jacket']
    }
    
    try:
        response = requests.post(f"{base_url}/chat", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_similarity_scores():
    """Test to see similarity scores in action"""
    print("\n\n🔍 Testing Similarity Scoring\n" + "="*50)
    
    # Create very similar images
    base_shirt = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(base_shirt)
    
    # Original
    draw.rectangle([(50, 40), (150, 160)], fill='red')
    original_b64 = image_to_base64(base_shirt)
    
    # Similar (different shade)
    similar_shirt = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(similar_shirt)
    draw.rectangle([(50, 40), (150, 160)], fill='darkred')
    similar_b64 = image_to_base64(similar_shirt)
    
    # Different (jacket)
    different = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(different)
    draw.rectangle([(40, 30), (160, 180)], fill='blue')
    different_b64 = image_to_base64(different)
    
    base_url = "http://localhost:8000"
    
    for name, image_b64 in [("Original Red Shirt", original_b64), 
                           ("Similar Dark Red Shirt", similar_b64), 
                           ("Different Blue Item", different_b64)]:
        print(f"\nTesting with: {name}")
        
        response = requests.post(
            f"{base_url}/chat",
            json={"message": "Find exact matches", "image": image_b64},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Products found:")
            if 'products' in data and data['products']:
                for p in data['products'][:2]:
                    print(f"  - {p['name']} (Similarity: {p.get('similarity_score', 'N/A')})")

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == "__main__":
    test_enhanced_image_search()
    test_similarity_scores()