import chromadb
from chromadb.utils import embedding_functions
import json
from typing import List, Dict, Optional
import numpy as np
from app.config import get_settings
from app.image_processor import ImageProcessor
from app.fashion_dataset import FashionDatasetLoader
import logging

logger = logging.getLogger(__name__)

class ProductVectorStore:
    def __init__(self):
        settings = get_settings()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        
        # Create embedding function for text
        self.text_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model
        )
        
        # Initialize components
        self.image_processor = ImageProcessor()
        self.dataset_loader = FashionDatasetLoader()
        
        # Get or create collections
        self.text_collection = self.client.get_or_create_collection(
            name="fashion_products_text",
            embedding_function=self.text_embedding_function
        )
        
        self.image_collection = self.client.get_or_create_collection(
            name="fashion_products_images",
            embedding_function=None
        )
        
        # Initialize with dataset if empty
        if self.text_collection.count() == 0:
            self._initialize_from_dataset()
    
    def _initialize_from_dataset(self):
        """Initialize vector store with fashion dataset"""
        print("Initializing vector store with fashion dataset...")
        
        # Get a sample of products (you can adjust the number)
        products = self.dataset_loader.get_random_products(500)
        
        text_documents = []
        text_metadatas = []
        text_ids = []
        
        image_embeddings = []
        image_metadatas = []
        image_ids = []
        
        for product in products:
            # Prepare text embedding data
            doc = f"{product['name']} {product['description']} {product['category']} {product['brand']} {product['color']} {' '.join(product['features'])}"
            
            # ChromaDB only accepts str, int, float, or None - convert booleans to strings
            metadata = {
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'price': float(product['price']),  # Ensure float
                'category': product['category'],
                'sub_category': product['sub_category'],
                'gender': product['gender'],
                'color': product['color'],
                'brand': product['brand'],
                'in_stock': str(product['in_stock']),  # Convert bool to string
                'features': json.dumps(product['features'])
            }
            
            text_documents.append(doc)
            text_metadatas.append(metadata)
            text_ids.append(product['id'])
            
            # Generate image embedding if image exists
            if product.get('image'):
                try:
                    # Convert PIL image to base64
                    image_base64 = self.dataset_loader.image_to_base64(product['image'])
                    # Generate embedding
                    embedding = self.image_processor.get_image_embedding(image_base64)
                    
                    image_embeddings.append(embedding)
                    image_metadatas.append(metadata.copy())  # Use same metadata
                    image_ids.append(f"{product['id']}_img")
                except Exception as e:
                    logger.error(f"Error processing image for {product['id']}: {e}")
        
        # Add to collections
        if text_documents:
            self.text_collection.add(
                documents=text_documents,
                metadatas=text_metadatas,
                ids=text_ids
            )
            logger.info(f"Added {len(text_documents)} products to text collection")
        
        if image_embeddings:
            self.image_collection.add(
                embeddings=image_embeddings,
                metadatas=image_metadatas,
                ids=image_ids
            )
            logger.info(f"Added {len(image_embeddings)} products to image collection")
    
    def search_products(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for products by text query"""
        try:
            # First try vector search
            results = self.text_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results and results['metadatas']:
                products = []
                for metadata in results['metadatas'][0]:
                    product = metadata.copy()
                    
                    # Convert back from strings
                    if 'features' in product and product['features']:
                        product['features'] = json.loads(product['features'])
                    if 'in_stock' in product:
                        product['in_stock'] = product['in_stock'] == 'True'
                    
                    # Get the full product with image from dataset
                    full_product = self.dataset_loader.get_product_by_id(product['id'])
                    if full_product and full_product.get('image'):
                        product['image_base64'] = self.dataset_loader.image_to_base64(full_product['image'])
                    
                    products.append(product)
                return products
            
            # Fallback to dataset search if vector search returns nothing
            dataset_results = self.dataset_loader.search_products(query, limit=n_results)
            return [self.dataset_loader.get_product_with_base64_image(p) for p in dataset_results]
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            # Fallback to dataset search
            dataset_results = self.dataset_loader.search_products(query, limit=n_results)
            return [self.dataset_loader.get_product_with_base64_image(p) for p in dataset_results]
    
    def search_by_image_embedding(self, image_embedding: List[float], n_results: int = 5) -> List[Dict]:
        """Search for products by image embedding"""
        try:
            results = self.image_collection.query(
                query_embeddings=[image_embedding],
                n_results=n_results
            )
            
            if results and results['metadatas']:
                products = []
                distances = results.get('distances', [[]])[0]
                
                for i, metadata in enumerate(results['metadatas'][0]):
                    product = metadata.copy()
                    
                    # Convert back from strings
                    if 'features' in product and product['features']:
                        product['features'] = json.loads(product['features'])
                    if 'in_stock' in product:
                        product['in_stock'] = product['in_stock'] == 'True'
                    
                    # Add similarity score
                    if i < len(distances):
                        similarity = 1 / (1 + distances[i])
                        product['similarity_score'] = round(similarity, 3)
                    
                    # Get the full product with image
                    full_product = self.dataset_loader.get_product_by_id(product['id'])
                    if full_product and full_product.get('image'):
                        product['image_base64'] = self.dataset_loader.image_to_base64(full_product['image'])
                    
                    products.append(product)
                
                products.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
                return products
            
            # If no results, return random products as fallback
            random_products = self.dataset_loader.get_random_products(n_results)
            return [self.dataset_loader.get_product_with_base64_image(p) for p in random_products]
            
        except Exception as e:
            logger.error(f"Error searching by image: {e}")
            # Fallback to random products
            random_products = self.dataset_loader.get_random_products(n_results)
            return [self.dataset_loader.get_product_with_base64_image(p) for p in random_products]