import redis
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Redis client wrapper for semantic caching.
    Handles connection management and basic operations.
    """
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = settings.REDIS_ENABLED
        
        if self.enabled:
            self._connect()
    
    def _connect(self):
        """Initialize Redis connection."""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,  # Auto-decode bytes to strings
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis connected successfully: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
            self.enabled = False
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            self.client = None
            self.enabled = False
    
    def health_check(self) -> dict:
        """Check Redis connection health."""
        if not self.enabled or not self.client:
            return {"connected": False, "message": "Redis disabled or not connected"}
        
        try:
            self.client.ping()
            return {"connected": True, "message": "Redis OK"}
        except:
            return {"connected": False, "message": "Redis connection lost"}
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.enabled or not self.client:
            return None
        
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set value in Redis with optional TTL."""
        if not self.enabled or not self.client:
            return
        
        try:
            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
    
    def delete(self, key: str):
        """Delete key from Redis."""
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
    
    def flushdb(self):
        """Flush all keys in current database."""
        if not self.enabled or not self.client:
            logger.warning("Redis not enabled, cannot flush")
            return
        
        try:
            self.client.flushdb()
            logger.info("Redis cache flushed successfully")
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
    
    def keys(self, pattern: str = "*"):
        """Get all keys matching pattern."""
        if not self.enabled or not self.client:
            return []
        
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

# Singleton instance
redis_cache = RedisCache()
