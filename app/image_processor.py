from PIL import Image
import base64
import io
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import List, Optional
import logging
from app.image_cache import ImageEmbeddingCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        try:
            # Load CLIP model for image embeddings
            self.model = SentenceTransformer('clip-ViT-B-32')
            logger.info("CLIP model loaded successfully")
            self.cache = ImageEmbeddingCache()
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            raise
    
    def base64_to_image(self, base64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            return image
        except Exception as e:
            logger.error(f"Error converting base64 to image: {e}")
            raise
    
    def get_image_embedding(self, base64_string: str) -> List[float]:
        """Generate embedding from base64 image with caching"""
        # Check cache first
        cached_embedding = self.cache.get_embedding(base64_string)
        if cached_embedding:
            logger.info("Using cached image embedding")
            return cached_embedding
        
        try:
            image = self.base64_to_image(base64_string)
            
            # Resize image for consistent processing
            image = image.resize((224, 224))
            
            # Generate embedding
            embedding = self.model.encode(image)
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            # Cache the result
            self.cache.set_embedding(base64_string, embedding.tolist())
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating image embedding: {e}")
            raise

    def get_text_embedding(self, text: str) -> List[float]:
        """Generate embedding from text (CLIP is multimodal)"""
        try:
            embedding = self.model.encode(text)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            raise