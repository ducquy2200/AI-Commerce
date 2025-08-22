from datasets import load_dataset
import numpy as np
from typing import List, Dict, Optional
import logging
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class FashionDatasetLoader:
    def __init__(self):
        print("Loading fashion dataset from HuggingFace...")
        self.dataset = load_dataset("ashraq/fashion-product-images-small", split="train")
        print(f"Loaded {len(self.dataset)} products")
        
        # Create indices for quick lookup
        self._create_indices()
        
    def _create_indices(self):
        """Create indices for efficient searching"""
        self.products_by_id = {}
        self.products_by_category = {}
        self.products_by_gender = {}
        self.products_by_color = {}
        self.all_products = []
        
        for idx, item in enumerate(self.dataset):
            product = self._format_product(item, idx)
            
            # Index by ID
            self.products_by_id[product['id']] = product
            self.all_products.append(product)
            
            # Index by category
            category = product['category']
            if category not in self.products_by_category:
                self.products_by_category[category] = []
            self.products_by_category[category].append(product)
            
            # Index by gender
            gender = product.get('gender', 'Unisex')
            if gender not in self.products_by_gender:
                self.products_by_gender[gender] = []
            self.products_by_gender[gender].append(product)
            
            # Index by color
            color = product.get('color', 'Unknown')
            if color not in self.products_by_color:
                self.products_by_color[color] = []
            self.products_by_color[color].append(product)
    
    def _format_product(self, item: Dict, idx: int) -> Dict:
        """Format HuggingFace dataset item to our product format"""
        # Generate a realistic price based on category
        price = self._generate_price(item.get('masterCategory', 'Other'))
        
        return {
            'id': f"prod_{item.get('id', idx)}",
            'name': item.get('productDisplayName', 'Fashion Product'),
            'description': self._generate_description(item),
            'price': price,
            'category': item.get('masterCategory', 'Other'),
            'sub_category': item.get('subCategory', 'Other'),
            'article_type': item.get('articleType', 'Other'),
            'gender': item.get('gender', 'Unisex'),
            'color': item.get('baseColour', 'Multi'),
            'season': item.get('season', 'All'),
            'usage': item.get('usage', 'Casual'),
            'brand': item.get('brandName', 'Generic'),
            'year': item.get('year', 2020),
            'image': item.get('image'),  # PIL Image object
            'in_stock': np.random.choice([True, False], p=[0.9, 0.1]),
            'features': [
                item.get('articleType', ''),
                item.get('baseColour', ''),
                item.get('season', ''),
                item.get('usage', ''),
                item.get('gender', '')
            ]
        }
    
    def _generate_price(self, category: str) -> float:
        """Generate realistic price based on category"""
        price_ranges = {
            'Apparel': (15, 150),
            'Footwear': (30, 300),
            'Accessories': (10, 100),
            'Personal Care': (5, 50),
            'Free Items': (0, 0),
            'Sporting Goods': (20, 200),
            'Home': (10, 100)
        }
        
        min_price, max_price = price_ranges.get(category, (20, 100))
        if min_price == max_price:
            return 0.0
        
        price = np.random.uniform(min_price, max_price)
        return round(price, 2)
    
    def _generate_description(self, item: Dict) -> str:
        """Generate product description"""
        parts = []
        
        if item.get('productDisplayName'):
            parts.append(item['productDisplayName'])
        
        if item.get('brandName') and item.get('articleType'):
            parts.append(f"This {item['brandName']} {item['articleType']} is perfect for your wardrobe")
        
        if item.get('baseColour') and item.get('season'):
            parts.append(f"Features {item['baseColour']} color, ideal for {item['season']} season")
        
        if item.get('usage'):
            parts.append(f"Great for {item['usage']} occasions")
        
        return ". ".join(parts) if parts else "High-quality fashion item"
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a single product by ID"""
        return self.products_by_id.get(product_id)
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple text search across products"""
        query_lower = query.lower()
        results = []
        
        for product in self.all_products:
            # Search in name, description, category, brand, color
            searchable_text = f"{product['name']} {product['description']} {product['category']} {product['brand']} {product['color']}".lower()
            
            if query_lower in searchable_text:
                results.append(product)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_products_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get products by category"""
        products = self.products_by_category.get(category, [])
        return products[:limit]
    
    def get_products_by_filters(self, filters: Dict, limit: int = 10) -> List[Dict]:
        """Get products by multiple filters"""
        results = self.all_products
        
        if 'category' in filters:
            results = [p for p in results if p['category'] == filters['category']]
        
        if 'gender' in filters:
            results = [p for p in results if p['gender'] == filters['gender']]
        
        if 'color' in filters:
            results = [p for p in results if p['color'] == filters['color']]
        
        if 'min_price' in filters:
            results = [p for p in results if p['price'] >= filters['min_price']]
        
        if 'max_price' in filters:
            results = [p for p in results if p['price'] <= filters['max_price']]
        
        return results[:limit]
    
    def get_random_products(self, n: int = 10) -> List[Dict]:
        """Get random products"""
        indices = np.random.choice(len(self.all_products), min(n, len(self.all_products)), replace=False)
        return [self.all_products[i] for i in indices]
    
    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def get_product_with_base64_image(self, product: Dict) -> Dict:
        """Add base64 image to product dict"""
        product_copy = product.copy()
        if product.get('image'):
            product_copy['image_base64'] = self.image_to_base64(product['image'])
        return product_copy