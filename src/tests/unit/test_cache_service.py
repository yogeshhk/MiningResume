"""
Unit tests for cache service.
"""

import pytest
import time

from llm_parser.services.cache_service import (
    InMemoryCacheService,
    CacheKeyGenerator,
    create_cache_service,
)


class TestInMemoryCacheService:
    """Tests for InMemoryCacheService."""

    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = InMemoryCacheService(default_ttl_seconds=60)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        cache = InMemoryCacheService()

        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = InMemoryCacheService(default_ttl_seconds=1)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        """Test custom TTL per key."""
        cache = InMemoryCacheService(default_ttl_seconds=60)

        cache.set("key1", "value1", ttl_seconds=1)
        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self):
        """Test deleting a key."""
        cache = InMemoryCacheService()

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.delete("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        """Test clearing all entries."""
        cache = InMemoryCacheService()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = InMemoryCacheService(default_ttl_seconds=1)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        time.sleep(1.1)

        removed = cache.cleanup_expired()
        assert removed == 2
        assert cache.get("key1") is None

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = InMemoryCacheService()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["size_bytes"] > 0


class TestCacheKeyGenerator:
    """Tests for CacheKeyGenerator."""

    def test_generate_key_consistency(self):
        """Test that same inputs generate same key."""
        key1 = CacheKeyGenerator.generate_key("prompt", "context", "attr")
        key2 = CacheKeyGenerator.generate_key("prompt", "context", "attr")

        assert key1 == key2

    def test_generate_key_uniqueness(self):
        """Test that different inputs generate different keys."""
        key1 = CacheKeyGenerator.generate_key("prompt1", "context", "attr")
        key2 = CacheKeyGenerator.generate_key("prompt2", "context", "attr")

        assert key1 != key2

    def test_generate_key_from_text(self):
        """Test generating key from text."""
        key = CacheKeyGenerator.generate_key_from_text("test text")

        assert isinstance(key, str)
        assert len(key) == 64  # SHA256 hex digest


class TestCreateCacheService:
    """Tests for cache service factory."""

    def test_create_memory_cache(self):
        """Test creating in-memory cache."""
        cache = create_cache_service("memory", 60)

        assert isinstance(cache, InMemoryCacheService)

    def test_create_unsupported_backend(self):
        """Test creating unsupported cache backend."""
        from llm_parser.core.exceptions import CacheError

        with pytest.raises(CacheError):
            create_cache_service("unsupported", 60)

