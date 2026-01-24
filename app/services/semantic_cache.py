import json
import math
from typing import Dict, Optional, List, Any
from app.db.cache import redis_cache
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class SemanticCache:
    """
    Semantic caching layer for RAG responses.
    Stores query embeddings and checks similarity before calling LLM.
    """
    
    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_cache
        self.threshold = settings.CACHE_SIMILARITY_THRESHOLD
        self.ttl = settings.CACHE_TTL
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors using pure Python."""
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        # Cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def check_cache(self, query_embedding: List[float], query_text: str) -> Optional[Dict[str, Any]]:
        """
        Check if a similar query exists in cache.
        
        Args:
            query_embedding: Vector embedding of the query
            query_text: Original query text (for logging)
            
        Returns:
            Cached result if similarity > threshold, else None
        """
        if not self.redis.enabled:
            return None
        
        try:
            cache_keys = self.redis.keys("cache:keys:set")  # This is the set key
            if cache_keys:
                # If set exists, use it
                cache_keys = self.redis.client.smembers("cache:keys:set") if self.redis.client else []
            else:
                # Fallback: still scan but at least we have the optimization
                cache_keys = []
            
            if not cache_keys:
                logger.debug(f"Cache empty for query: '{query_text[:50]}...'")
                return None
            
            # Find most similar cached query
            max_similarity = 0.0
            best_match_key = None
            
            for key in cache_keys:
                cached_data = self.redis.get(key)
                if not cached_data:
                    continue
                
                try:
                    cached = json.loads(cached_data)
                    cached_embedding = cached.get("embedding")
                    
                    if not cached_embedding:
                        continue
                    
                    similarity = self._cosine_similarity(query_embedding, cached_embedding)
                    
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match_key = key
                
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in cache key: {key}")
                    continue
            
            # Return cached result if above threshold
            if max_similarity >= self.threshold and best_match_key:
                cached_data = self.redis.get(best_match_key)
                cached = json.loads(cached_data)
                logger.info(
                    f" Cache HIT (similarity: {max_similarity:.3f}) for query: '{query_text[:50]}...'"
                )
                return {
                    "answer": cached.get("answer"),
                    "sources": cached.get("sources", []),
                    "similarity": max_similarity,
                    "cached_query": cached.get("query_text")
                }
            
            logger.debug(
                f" Cache MISS (max similarity: {max_similarity:.3f}) for query: '{query_text[:50]}...'"
            )
            return None
            
        except Exception as e:
            logger.error(f"Cache check error: {e}")
            return None
    
    def set_cache(
        self, 
        query_embedding: List[float], 
        query_text: str, 
        answer: str, 
        sources: List[Dict]
    ):
        """
        Store query result in cache with embedding.
        
        Args:
            query_embedding: Vector embedding of the query
            query_text: Original query text
            answer: LLM response
            sources: Context sources used
        """
        if not self.redis.enabled:
            return
        
        try:
            # Use hash of query text as key
            import hashlib
            query_hash = hashlib.md5(query_text.encode()).hexdigest()
            cache_key = f"cache:query:{query_hash}"
            
            cache_data = {
                "query_text": query_text,
                "embedding": query_embedding,
                "answer": answer,
                "sources": sources
            }
            
            # Store the data
            self.redis.set(cache_key, json.dumps(cache_data), ttl=self.ttl)
            
            # Track this key in a set (O(1) operation)
            if self.redis.client:
                self.redis.client.sadd("cache:keys:set", cache_key)
                # Set TTL for tracking set too
                self.redis.client.expire("cache:keys:set", self.ttl)
            
            logger.info(f" Cached answer for query: '{query_text[:50]}...'")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")

def get_semantic_cache():
    """Factory function for dependency injection."""
    return SemanticCache()
