"""
AI Response Cache Manager
Reduces OpenAI API calls by caching responses and implementing smart fallbacks
"""

import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    response: str
    timestamp: datetime
    data_hash: str
    hit_count: int = 0
    ttl_seconds: int = 3600  # 1 hour default

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)

    def is_fresh(self, max_age_seconds: int = 300) -> bool:
        """Check if cache entry is fresh (within max_age)"""
        return datetime.now() < self.timestamp + timedelta(seconds=max_age_seconds)

class AIResponseCache:
    """In-memory cache for AI responses with intelligent invalidation"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'api_calls_saved': 0
        }
    
    def _generate_cache_key(self, data: Dict[str, Any], prompt_type: str, **kwargs) -> str:
        """Generate cache key from data and parameters"""
        # Create a stable hash from data content
        data_str = json.dumps(data, sort_keys=True, default=str)
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        combined = f"{prompt_type}:{data_str}:{params_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash of data content for change detection"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, data: Dict[str, Any], prompt_type: str, **kwargs) -> Optional[str]:
        """Get cached response if available and valid"""
        cache_key = self._generate_cache_key(data, prompt_type, **kwargs)
        
        if cache_key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[cache_key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[cache_key]
            self.stats['misses'] += 1
            return None
        
        # Check if data has changed significantly
        current_data_hash = self._generate_data_hash(data)
        if entry.data_hash != current_data_hash:
            # Data changed, invalidate cache
            del self.cache[cache_key]
            self.stats['misses'] += 1
            return None
        
        # Cache hit
        entry.hit_count += 1
        self.stats['hits'] += 1
        self.stats['api_calls_saved'] += 1
        
        logger.info(f"Cache hit for {prompt_type} (saved API call)")
        return entry.response
    
    def set(self, data: Dict[str, Any], prompt_type: str, response: str, ttl_seconds: int = 3600, **kwargs):
        """Store response in cache"""
        cache_key = self._generate_cache_key(data, prompt_type, **kwargs)
        data_hash = self._generate_data_hash(data)
        
        # Evict oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[cache_key] = CacheEntry(
            response=response,
            timestamp=datetime.now(),
            data_hash=data_hash,
            ttl_seconds=ttl_seconds
        )
        
        logger.info(f"Cached response for {prompt_type}")
    
    def _evict_oldest(self):
        """Evict oldest cache entries"""
        if not self.cache:
            return
        
        # Sort by timestamp and remove oldest 10%
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].timestamp
        )
        
        evict_count = max(1, len(sorted_entries) // 10)
        for i in range(evict_count):
            key = sorted_entries[i][0]
            del self.cache[key]
            self.stats['evictions'] += 1
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.cache[key]
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries matching '{pattern}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")

# Global cache instance
ai_cache = AIResponseCache()

def cached_ai_response(prompt_type: str, ttl_seconds: int = 3600, use_fresh_threshold: int = 300):
    """
    Decorator for caching AI responses
    
    Args:
        prompt_type: Type of prompt for cache key generation
        ttl_seconds: Time to live for cache entries
        use_fresh_threshold: Use cached response if fresher than this (seconds)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, data: Dict[str, Any], *args, **kwargs):
            # Check cache first
            cached_response = ai_cache.get(data, prompt_type, **kwargs)
            if cached_response:
                return cached_response
            
            # Check if we have a slightly stale but acceptable response
            cache_key = ai_cache._generate_cache_key(data, prompt_type, **kwargs)
            if cache_key in ai_cache.cache:
                entry = ai_cache.cache[cache_key]
                if entry.is_fresh(use_fresh_threshold):
                    logger.info(f"Using fresh cached response for {prompt_type}")
                    entry.hit_count += 1
                    ai_cache.stats['hits'] += 1
                    return entry.response
            
            # Generate new response
            try:
                response = func(self, data, *args, **kwargs)
                if response:
                    ai_cache.set(data, prompt_type, response, ttl_seconds, **kwargs)
                return response
            except Exception as e:
                logger.error(f"Error generating AI response for {prompt_type}: {e}")
                # Try to return stale cache as fallback
                if cache_key in ai_cache.cache:
                    logger.info(f"Using stale cache as fallback for {prompt_type}")
                    return ai_cache.cache[cache_key].response
                raise
        
        return wrapper
    return decorator

class RequestBatcher:
    """Batch multiple similar requests to reduce API calls"""
    
    def __init__(self, batch_size: int = 5, batch_timeout: float = 2.0):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests: Dict[str, list] = {}
        self.batch_timers: Dict[str, float] = {}
    
    def add_request(self, request_type: str, data: Dict[str, Any], callback):
        """Add request to batch"""
        if request_type not in self.pending_requests:
            self.pending_requests[request_type] = []
            self.batch_timers[request_type] = time.time()
        
        self.pending_requests[request_type].append({
            'data': data,
            'callback': callback,
            'timestamp': time.time()
        })
        
        # Process batch if full or timeout reached
        if (len(self.pending_requests[request_type]) >= self.batch_size or
            time.time() - self.batch_timers[request_type] > self.batch_timeout):
            self._process_batch(request_type)
    
    def _process_batch(self, request_type: str):
        """Process batched requests"""
        if request_type not in self.pending_requests:
            return
        
        requests = self.pending_requests[request_type]
        del self.pending_requests[request_type]
        del self.batch_timers[request_type]
        
        logger.info(f"Processing batch of {len(requests)} {request_type} requests")
        
        # Process requests (implementation depends on request type)
        for request in requests:
            try:
                # This would be implemented based on specific request types
                request['callback'](request['data'])
            except Exception as e:
                logger.error(f"Error processing batched request: {e}")

# Global request batcher
request_batcher = RequestBatcher()
