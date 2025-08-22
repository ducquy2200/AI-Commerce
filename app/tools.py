from langchain.tools import Tool
from typing import Optional, List, Dict
from app.vector_store import ProductVectorStore
from app.image_processor import ImageProcessor
import logging

logger = logging.getLogger(__name__)

# Initialize components
vector_store = ProductVectorStore()
image_processor = ImageProcessor()

# Store for current image (will be set by the agent)
current_image_store = {"image": None}

def load_sample_products():
    """Load sample products into vector store"""
    sample_products = [
        {
            "id": "prod_001",
            "name": "Nike Dri-FIT Sports T-Shirt",
            "description": "High-performance athletic t-shirt with moisture-wicking technology",
            "price": 39.99,
            "category": "Sportswear",
            "features": ["moisture-wicking", "breathable", "athletic fit", "nike", "t-shirt", "sports"],
            "image_description": "Red Nike sports t-shirt with swoosh logo, athletic fit design"
        },
        {
            "id": "prod_002",
            "name": "Adidas Performance Running Tee",
            "description": "Lightweight running shirt with AEROREADY technology",
            "price": 44.99,
            "category": "Sportswear",
            "features": ["running", "lightweight", "quick-dry", "adidas", "performance"],
            "image_description": "Blue Adidas running t-shirt with three stripes, athletic wear"
        },
        {
            "id": "prod_003",
            "name": "Under Armour HeatGear Tank",
            "description": "Compression tank top for intense workouts",
            "price": 34.99,
            "category": "Sportswear",
            "features": ["compression", "tank top", "workout", "under armour", "gym"],
            "image_description": "Black Under Armour tank top, compression fit for gym workouts"
        },
        {
            "id": "prod_004",
            "name": "Levi's Classic Denim Jacket",
            "description": "Timeless denim jacket with authentic vintage styling",
            "price": 89.99,
            "category": "Outerwear",
            "features": ["denim", "jacket", "casual", "levi's"],
            "image_description": "Classic blue denim jacket with button front, Levi's style"
        },
        {
            "id": "prod_005",
            "name": "Columbia Rain Jacket",
            "description": "Waterproof and breathable rain jacket for outdoor adventures",
            "price": 79.99,
            "category": "Outerwear",
            "features": ["waterproof", "rain jacket", "outdoor", "columbia"],
            "image_description": "Green Columbia rain jacket with hood, waterproof outdoor gear"
        }
    ]
    
    # Check if products already exist - check text_collection instead of collection
    try:
        existing = vector_store.text_collection.count()
        if existing == 0:
            vector_store.add_products_with_images(sample_products)
            logger.info(f"Loaded {len(sample_products)} sample products")
        else:
            logger.info(f"Products already exist in vector store ({existing} items)")
    except Exception as e:
        logger.error(f"Error loading sample products: {e}")
        # Try to add products anyway
        try:
            vector_store.add_products_with_images(sample_products)
            logger.info(f"Loaded {len(sample_products)} sample products")
        except Exception as inner_e:
            logger.error(f"Failed to load products: {inner_e}")

# Tool functions
def general_chat(query: str) -> str:
    """Handle general conversation that doesn't require product search"""
    responses = {
        "name": "I'm CommerceAI, your AI shopping assistant!",
        "help": "I can help you find products, answer questions about items, and provide personalized recommendations.",
        "capabilities": "I can search for products by description or analyze images to find similar items.",
        "greeting": "Hello! I'm here to help you find the perfect products. What are you looking for today?"
    }
    
    query_lower = query.lower()
    
    if "name" in query_lower:
        return responses["name"]
    elif "help" in query_lower or "do" in query_lower:
        return responses["help"]
    elif "capabilit" in query_lower or "can you" in query_lower:
        return responses["capabilities"]
    elif "hello" in query_lower or "hi" in query_lower:
        return responses["greeting"]
    
    return "I'm here to help you with your shopping needs. Feel free to ask me about products or upload an image to find similar items!"

def search_products(query: str) -> str:
    """Search for products based on text description"""
    try:
        products = vector_store.search_products(query, n_results=5)
        
        if not products:
            # Try searching directly in dataset
            products = vector_store.dataset_loader.search_products(query, limit=5)
            products = [vector_store.dataset_loader.get_product_with_base64_image(p) for p in products]
        
        if not products:
            return f"I couldn't find any products matching '{query}'. Try different keywords or browse our categories."
        
        response = f"I found {len(products)} products for '{query}':\n\n"
        for i, product in enumerate(products, 1):
            response += f"{i}. **{product['name']}**\n"
            response += f"   Brand: {product.get('brand', 'Unknown')}\n"
            response += f"   Price: ${product['price']}\n"
            response += f"   Color: {product.get('color', 'N/A')}\n"
            response += f"   Category: {product.get('category', 'N/A')}\n"
            response += f"   {product['description']}\n\n"
        
        return response
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return "I encountered an error while searching. Please try again."

def search_by_image(query: str) -> str:
    """Search for products similar to the provided image"""
    # Check if we have a current image
    if not current_image_store["image"]:
        return "Please upload an image first so I can find similar products."
    
    try:
        # Log what query we received
        logger.info(f"search_by_image called with query: '{query}'")
        
        # Get image embedding
        image_embedding = image_processor.get_image_embedding(current_image_store["image"])
        
        # Search for similar products
        products = vector_store.search_by_image_embedding(image_embedding, n_results=5)
        
        if not products:
            return "I couldn't find products similar to your image. Try uploading a different image."
        
        # Build response based on the query context
        if "shirt" in query.lower():
            response = "Based on your image, here are similar shirts:\n\n"
        elif "shoe" in query.lower() or "footwear" in query.lower():
            response = "Based on your image, here are similar footwear options:\n\n"
        elif "jacket" in query.lower():
            response = "Based on your image, here are similar jackets:\n\n"
        else:
            response = "Based on your image, here are similar products:\n\n"
        
        for i, product in enumerate(products, 1):
            response += f"{i}. **{product['name']}**\n"
            response += f"   Price: ${product['price']}\n"
            response += f"   {product['description']}\n"
            if product.get('similarity_score'):
                response += f"   Similarity: {product['similarity_score']*100:.1f}%\n"
            response += "\n"
        
        # Add contextual information
        if products[0].get('category'):
            categories = set(p.get('category') for p in products if p.get('category'))
            if categories:
                response += f"\nThese products are from: {', '.join(categories)}"
        
        # Add context from the query if relevant
        if "color" in query.lower():
            response += "\n\nNote: Color matching is based on the overall appearance of the uploaded image."
        elif "style" in query.lower():
            response += "\n\nNote: I've found products with similar style and design elements."
        
        return response
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return "I had trouble processing your image. Please make sure it's a valid image file and try again."

# Create tools list
def create_tools():
    """Create and return the list of tools"""
    return [
        Tool(
            name="general_chat",
            func=general_chat,
            description="Use this for general conversation and questions not related to product search. Use when users ask about your name, capabilities, or general help."
        ),
        Tool(
            name="search_products",
            func=search_products,
            description="Use this to search for products based on text descriptions. Use when users ask for specific products, categories, or features."
        ),
        Tool(
            name="search_by_image",
            func=search_by_image,
            description="Use this to find products similar to an uploaded image. The query should describe what aspect of the image to focus on (e.g., 'similar shirts', 'same style', 'matching color'). Only use when the user has uploaded an image."
        )
    ]

# Initialize products on module load
try:
    load_sample_products()
except Exception as e:
    logger.error(f"Error during initial product load: {e}")
    print(f"Warning: Could not load sample products: {e}")