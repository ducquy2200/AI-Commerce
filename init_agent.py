"""
Initialize the agent with sample data including image descriptions
"""
from app.vector_store import ProductVectorStore
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_products_with_images():
    """Load products with image descriptions for CLIP embeddings"""
    products = [
        {
            "id": "prod_001",
            "name": "Nike Dri-FIT Sports T-Shirt",
            "description": "High-performance athletic t-shirt with moisture-wicking technology",
            "price": 39.99,
            "category": "Sportswear",
            "features": ["moisture-wicking", "breathable", "athletic fit", "nike", "t-shirt", "sports"],
            "image_url": "/images/nike-drifit.jpg",
            "image_description": "Red Nike sports t-shirt with swoosh logo, athletic fit design"
        },
        {
            "id": "prod_002",
            "name": "Adidas Performance Running Tee",
            "description": "Lightweight running shirt with AEROREADY technology",
            "price": 44.99,
            "category": "Sportswear",
            "features": ["running", "lightweight", "quick-dry", "adidas", "performance"],
            "image_url": "/images/adidas-running.jpg",
            "image_description": "Blue Adidas running t-shirt with three stripes, athletic wear"
        },
        {
            "id": "prod_003",
            "name": "Under Armour HeatGear Tank",
            "description": "Compression tank top for intense workouts",
            "price": 34.99,
            "category": "Sportswear",
            "features": ["compression", "tank top", "workout", "under armour", "gym"],
            "image_url": "/images/ua-tank.jpg",
            "image_description": "Black Under Armour tank top, compression fit for gym workouts"
        },
        {
            "id": "prod_004",
            "name": "Levi's Classic Denim Jacket",
            "description": "Timeless denim jacket with authentic vintage styling",
            "price": 89.99,
            "category": "Outerwear",
            "features": ["denim", "jacket", "casual", "levi's", "vintage"],
            "image_url": "/images/levis-jacket.jpg",
            "image_description": "Classic blue denim jacket with button front, Levi's style"
        },
        {
            "id": "prod_005",
            "name": "Columbia Rain Jacket",
            "description": "Waterproof and breathable rain jacket for outdoor adventures",
            "price": 79.99,
            "category": "Outerwear",
            "features": ["waterproof", "rain jacket", "outdoor", "columbia", "hiking"],
            "image_url": "/images/columbia-rain.jpg",
            "image_description": "Green Columbia rain jacket with hood, waterproof outdoor gear"
        },
        {
            "id": "prod_006",
            "name": "Puma Running Shorts",
            "description": "Lightweight running shorts with inner brief",
            "price": 29.99,
            "category": "Sportswear",
            "features": ["running", "shorts", "lightweight", "puma", "athletic"],
            "image_url": "/images/puma-shorts.jpg",
            "image_description": "Black Puma running shorts with logo, athletic shorts for sports"
        },
        {
            "id": "prod_007",
            "name": "New Balance 990v5 Sneakers",
            "description": "Premium running shoes with superior cushioning",
            "price": 174.99,
            "category": "Footwear",
            "features": ["running shoes", "sneakers", "new balance", "cushioning", "premium"],
            "image_url": "/images/nb-990v5.jpg",
            "image_description": "Grey New Balance 990v5 sneakers, premium running shoes"
        },
        {
            "id": "prod_008",
            "name": "Champion Hoodie",
            "description": "Classic pullover hoodie with kangaroo pocket",
            "price": 49.99,
            "category": "Sportswear",
            "features": ["hoodie", "pullover", "champion", "casual", "comfortable"],
            "image_url": "/images/champion-hoodie.jpg",
            "image_description": "Grey Champion hoodie with logo, pullover sweatshirt with front pocket"
        }
    ]
    
    return products

if __name__ == "__main__":
    logger.info("Initializing product vector store with image embeddings...")
    
    # Initialize vector store
    vector_store = ProductVectorStore()
    
    # Clear existing data (optional)
    try:
        vector_store.text_collection.delete(where={})
        vector_store.image_collection.delete(where={})
        logger.info("Cleared existing collections")
    except:
        pass
    
    # Load products
    products = load_products_with_images()
    vector_store.add_products_with_images(products)
    
    logger.info(f"Successfully loaded {len(products)} products with image embeddings")
    
    # Test search
    logger.info("\nTesting text search...")
    results = vector_store.search_products("sports t-shirt", n_results=3)
    logger.info(f"Found {len(results)} results for 'sports t-shirt'")
    for product in results:
        logger.info(f"- {product['name']} (${product['price']})")
    
    # Test image search with text description
    logger.info("\nTesting image search with description...")
    test_embedding = vector_store.image_processor.get_text_embedding("red athletic shirt")
    image_results = vector_store.search_by_image_embedding(test_embedding, n_results=3)
    logger.info(f"Found {len(image_results)} similar products")
    for product in image_results:
        logger.info(f"- {product['name']} (similarity: {product.get('similarity_score', 'N/A')})")