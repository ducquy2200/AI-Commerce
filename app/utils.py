import base64
import imghdr
from typing import Optional
import logging
from datetime import datetime
import re
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_base64_image(image_string: str) -> tuple[bool, Optional[str]]:
    """
    Validate if a base64 string is a valid image
    """
    try:
        # Decode base64
        image_data = base64.b64decode(image_string)
        
        # Check image format
        image_format = imghdr.what(None, h=image_data)
        
        if image_format in ['jpeg', 'png', 'jpg']:
            return True, image_format
        else:
            return False, None
            
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return False, None

def create_session_id() -> str:
    """
    Create a unique session ID
    """
    import uuid
    return str(uuid.uuid4())

def format_product_response(products: list) -> str:
    """
    Format product list into a readable response
    """
    if not products:
        return "No products found."
    
    response = "Here are some products I found:\n\n"
    for i, product in enumerate(products, 1):
        response += f"{i}. **{product.get('name', 'Unknown')}**\n"
        response += f"   Price: ${product.get('price', 0):.2f}\n"
        response += f"   {product.get('description', 'No description available')}\n\n"
    
    return response

def log_api_request(endpoint: str, method: str, client_id: Optional[str] = None):
    """
    Log API requests for monitoring
    """
    logger.info(f"{datetime.now()} - {method} {endpoint} - Client: {client_id or 'Anonymous'}")

class RateLimiter:
    """
    Simple rate limiter for API endpoints
    """
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        
        # Clean old entries
        self.requests = {
            cid: timestamps for cid, timestamps in self.requests.items()
            if timestamps and (now - timestamps[-1]).seconds < self.window_seconds
        }
        
        # Check current client
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Filter timestamps within window
        client_requests = [
            ts for ts in self.requests[client_id]
            if (now - ts).seconds < self.window_seconds
        ]
        
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            self.requests[client_id] = client_requests
            return True
        
        return False
    
def extract_products_from_response(response: str) -> List[Dict]:
    """Extract product information from agent response"""
    products = []
    
    # Pattern to match product listings in the response
    product_pattern = r'\d+\.\s+\*\*(.*?)\*\*\s+Price:\s+\$([\d.]+)\s+(.*?)(?=\d+\.|$)'
    
    matches = re.finditer(product_pattern, response, re.DOTALL)
    
    for match in matches:
        product = {
            "name": match.group(1).strip(),
            "price": float(match.group(2)),
            "description": match.group(3).strip()
        }
        products.append(product)
    
    return products

def format_product_cards(products: List[Dict]) -> str:
    """Format products for display in chat"""
    if not products:
        return ""
    
    cards = []
    for product in products:
        card = f"""
**{product['name']}**
💰 ${product['price']:.2f}
📝 {product['description']}
🛒 [Add to Cart](#) | 👁️ [View Details](#)
---"""
        cards.append(card)
    
    return "\n".join(cards)

def clean_agent_response(response: str) -> Tuple[str, List[Dict]]:
    """Clean agent response and extract products"""
    # Extract products from response
    products = extract_products_from_response(response)
    
    # Clean the response text (remove duplicate product listings if we're showing cards)
    if products:
        # Remove the product listings from the text since we'll show them as cards
        cleaned_response = re.sub(r'\d+\.\s+\*\*.*?\*\*.*?(?=\d+\.|$)', '', response, flags=re.DOTALL)
        cleaned_response = cleaned_response.strip()
        
        # Add a message if only products remain
        if not cleaned_response or cleaned_response.isspace():
            cleaned_response = "Here are the products I found for you:"
    else:
        cleaned_response = response
    
    return cleaned_response, products
