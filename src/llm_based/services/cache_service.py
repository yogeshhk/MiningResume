"""
Cache service for storing and retrieving LLM responses.

Provides in-memory caching with TTL support.
"""

import time
import hashlib
from typing import Optional, Dict, Tuple
from threading import Lock

from src.llm_based.core.interfaces import ICacheService
from src.llm_based.core.exceptions import CacheError
from src.llm_based.utils.logger import get_logger
from src.llm_based.config.settings import settings

logger = get_logger(__name__)


class InMemoryCacheService(ICacheService):
    """In-memory cache implementation with TTL support."""

    def __init__(self):
        """
        Initialize in-memory cache.
        """
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._lock = Lock()
        logger.info("Initialized in-memory cache service", default_ttl=settings.cache_ttl_seconds)

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                logger.debug("Cache miss", key=key)
                return None

            value, expiry_time = self._cache[key]

            # Check if expired
            if time.time() > expiry_time:
                logger.debug("Cache expired", key=key)
                del self._cache[key]
                return None

            logger.debug("Cache hit", key=key)
            return value

    def set(self, key: str, value: str, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (uses default if None)
        """
        ttl = ttl_seconds if ttl_seconds is not None else settings.ttl_seconds
        expiry_time = time.time() + ttl

        with self._lock:
            self._cache[key] = (value, expiry_time)
            logger.debug("Cache set", key=key, ttl_seconds=ttl)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info("Cache cleared", entries_removed=count)

    def delete(self, key: str) -> None:
        """
        Delete a specific cache entry.

        Args:
            key: Cache key to delete
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("Cache entry deleted", key=key)

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time > expiry
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug("Expired cache entries removed", count=len(expired_keys))

            return len(expired_keys)

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            return {
                "total_entries": len(self._cache),
                "size_bytes": sum(
                    len(key) + len(value)
                    for key, (value, _) in self._cache.items()
                ),
            }


class CacheKeyGenerator:
    """Utility for generating consistent cache keys."""

    @staticmethod
    def generate_key(prompt: str, context: str, attribute: str) -> str:
        """
        Generate a cache key from prompt components.

        Args:
            prompt: The prompt template
            context: The resume text
            attribute: The attribute being extracted

        Returns:
            Cache key as hex digest
        """
        # Combine all components
        combined = f"{prompt}|{context}|{attribute}"

        # Generate hash
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        cache_key = hash_obj.hexdigest()

        return cache_key

    @staticmethod
    def generate_key_from_text(text: str) -> str:
        """
        Generate a cache key from arbitrary text.

        Args:
            text: Text to generate key from

        Returns:
            Cache key as hex digest
        """
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        return hash_obj.hexdigest()


# Factory function for cache service
def create_cache_service(
    **kwargs
) -> ICacheService:
    """
    Create a cache service instance.

    Args:
        **kwargs: Additional backend-specific arguments

    Returns:
        ICacheService implementation

    Raises:
        CacheError: If backend is not supported
    """
    if settings.cache_backend .lower() == "memory":
        return InMemoryCacheService()
    elif settings.cache_backend.lower() == "redis":
        # Placeholder for Redis implementation
        logger.warning("Redis cache not implemented, falling back to in-memory cache")
        return InMemoryCacheService()
    else:
        raise CacheError(
            f"Unsupported cache backend: {settings.cache_backend}",
            details={"backend": settings.cache_backend, "supported_backends": ["memory", "redis"]}
        )

