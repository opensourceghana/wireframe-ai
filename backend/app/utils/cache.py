"""
Simple caching utilities
"""

import time
import hashlib
from typing import Any, Optional, Dict
from ..core.config import settings


class CacheManager:
    """Simple in-memory cache for wireframe generation"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.enabled = settings.enable_caching
        self.ttl = settings.cache_ttl
    
    def _generate_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters"""
        # Create a hash of the prompt and parameters
        content = f"{prompt}:{sorted(kwargs.items())}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, **kwargs) -> Optional[Any]:
        """Get cached wireframe if available"""
        if not self.enabled:
            return None
        
        key = self._generate_key(prompt, **kwargs)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # Check if expired
            if time.time() - entry["timestamp"] > self.ttl:
                del self._cache[key]
                return None
            
            return entry["data"]
        
        return None
    
    def set(self, prompt: str, data: Any, **kwargs):
        """Cache wireframe data"""
        if not self.enabled:
            return
        
        key = self._generate_key(prompt, **kwargs)
        
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
        
        # Simple cleanup - remove oldest entries if cache gets too large
        if len(self._cache) > 100:  # Max 100 cached items
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "enabled": self.enabled,
            "entries": len(self._cache),
            "ttl": self.ttl
        }
