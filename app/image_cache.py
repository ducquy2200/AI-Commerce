import hashlib
from typing import Dict, List, Optional
import json
import os

class ImageEmbeddingCache:
    def __init__(self, cache_file: str = "image_cache.json"):
        self.cache_file = cache_file
        self.cache: Dict[str, List[float]] = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}
    
    def save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get_image_hash(self, base64_image: str) -> str:
        """Generate hash for image"""
        return hashlib.md5(base64_image.encode()).hexdigest()
    
    def get_embedding(self, base64_image: str) -> Optional[List[float]]:
        """Get cached embedding if exists"""
        image_hash = self.get_image_hash(base64_image)
        return self.cache.get(image_hash)
    
    def set_embedding(self, base64_image: str, embedding: List[float]):
        """Cache an embedding"""
        image_hash = self.get_image_hash(base64_image)
        self.cache[image_hash] = embedding
        self.save_cache()