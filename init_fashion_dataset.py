"""
Initialize the vector store with fashion dataset
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.vector_store import ProductVectorStore
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Initializing Fashion Product Vector Store...")
    print("This may take a few minutes on first run as it downloads the dataset from HuggingFace...")
    
    # Initialize vector store (this will automatically load from HuggingFace)
    vector_store = ProductVectorStore()
    
    print("\nTesting the setup...")
    
    # Test search
    results = vector_store.search_products("red dress", n_results=3)
    print(f"\nFound {len(results)} products for 'red dress':")
    for product in results:
        print(f"- {product['name']} (${product['price']}) - {product['brand']}")
    
    print("\n✅ Fashion dataset initialized successfully!")
    print(f"Total products in text collection: {vector_store.text_collection.count()}")
    print(f"Total products in image collection: {vector_store.image_collection.count()}")