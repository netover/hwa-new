import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from resync.core.cache_hierarchy import (
    CacheHierarchy,
    CacheMetrics,
    L1Cache,
    get_cache_hierarchy,
)


class TestL1Cache:
    """Test L1 cache functionality."""

    @pytest.fixture
    def l1_cache(self):
        """Create L1 cache instance for testing."""
        return L1Cache(max_size=100)

    @pytest.mark.asyncio
    async def test_l1_basic_get_set(self, l1_cache):
        """Test basic get/set operations."""
        # Test set operation
        await l1_cache.set("test_key", "test_value")
        assert l1_cache.size() == 1

        # Test get operation
        value = await l1_cache.get("test_key")
        assert value == "test_value"

        # Test get non-existent key
        value = await l1_cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_l1_concurrent_access(self, l1_cache):
        """Test concurrent access to L1 cache."""
        # Add initial value
        await l1_cache.set("key1", "value1")

        async def getter():
            return await l1_cache.get("key1")

        async def setter():
            await l1_cache.set("key2", "value2")
            return await l1_cache.get("key2")

        # Run concurrent operations
        tasks = [getter(), getter(), setter()]
        results = await asyncio.gather(*tasks)

        assert results[0] == "value1"
        assert results[1] == "value1"
        assert results[2] == "value2"
        assert l1_cache.size() == 2

    @pytest.mark.asyncio
    async def test_l1_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Create cache with small size for testing
        small_cache = L1Cache(max_size=3)

        # Add 3 items
        await small_cache.set("key1", "value1")
        await small_cache.set("key2", "value2")
        await small_cache.set("key3", "value3")
        assert small_cache.size() == 3

        # Access key1 to make it most recently used
        await small_cache.get("key1")

        # Add 4th item - should evict LRU (key2)
        await small_cache.set("key4", "value4")
        assert small_cache.size() == 3

        # Check that key2 was evicted (LRU)
        assert await small_cache.get("key2") is None
        # Check that others still exist
        assert await small_cache.get("key1") == "value1"
        assert await small_cache.get("key3") == "value3"
        assert await small_cache.get("key4") == "value4"

    @pytest.mark.asyncio
    async def test_l1_delete_operations(self, l1_cache):
        """Test delete operations."""
        # Set multiple values
        await l1_cache.set("key1", "value1")
        await l1_cache.set("key2", "value2")
        assert l1_cache.size() == 2

        # Delete existing key
        result = await l1_cache.delete("key1")
        assert result is True
        assert l1_cache.size() == 1

        # Delete non-existent key
        result = await l1_cache.delete("nonexistent")
        assert result is False
        assert l1_cache.size() == 1

        # Verify remaining key
        assert await l1_cache.get("key2") == "value2"

    @pytest.mark.asyncio
    async def test_l1_clear_operations(self, l1_cache):
        """Test clear operations."""
        # Add some items
        await l1_cache.set("key1", "value1")
        await l1_cache.set("key2", "value2")
        assert l1_cache.size() == 2

        # Clear all items
        await l1_cache.clear()
        assert l1_cache.size() == 0

        # Verify all items are gone
        assert await l1_cache.get("key1") is None
        assert await l1_cache.get("key2") is None


class TestCacheMetrics:
    """Test cache metrics functionality."""

    def test_metrics_calculations(self):
        """Test metrics calculations."""
        metrics = CacheMetrics()

        # Test initial state
        assert metrics.l1_hit_ratio == 0.0
        assert metrics.l2_hit_ratio == 0.0
        assert metrics.overall_hit_ratio == 0.0

        # Add some hits and misses
        metrics.l1_hits = 80
        metrics.l1_misses = 20
        metrics.l2_hits = 15
        metrics.l2_misses = 5
        metrics.total_gets = 120
        metrics.total_sets = 30

        assert metrics.l1_hit_ratio == 0.8  # 80/100
        assert metrics.l2_hit_ratio == 0.75  # 15/20
        assert metrics.overall_hit_ratio == (80 + 15) / 120  # 95/120 = 0.7917


class TestCacheHierarchy:
    """Test cache hierarchy functionality."""

    @pytest.fixture
    async def cache_hierarchy(self):
        """Create cache hierarchy instance for testing."""
        cache = CacheHierarchy(
            l1_max_size=100, l2_ttl_seconds=30, l2_cleanup_interval=10
        )
        await cache.start()
        try:
            yield cache
        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_hierarchy_basic_operations(self, cache_hierarchy):
        """Test basic get/set operations in hierarchy."""
        # Test set operation
        await cache_hierarchy.set("test_key", "test_value")
        assert cache_hierarchy.metrics.total_sets == 1

        # Test get operation (should hit L1)
        value = await cache_hierarchy.get("test_key")
        assert value == "test_value"
        assert cache_hierarchy.metrics.total_gets == 1
        assert cache_hierarchy.metrics.l1_hits == 1

    @pytest.mark.asyncio
    async def test_hierarchy_write_through(self, cache_hierarchy):
        """Test write-through pattern."""
        # Set value
        await cache_hierarchy.set("write_key", "write_value")

        # Verify both caches have the value
        l1_size, l2_size = cache_hierarchy.size()
        assert l1_size >= 1  # L1 should have the entry
        assert l2_size >= 1  # L2 should have the entry

        # Get should hit L1
        value = await cache_hierarchy.get("write_key")
        assert value == "write_value"

    @pytest.mark.asyncio
    async def test_hierarchy_miss_scenario(self, cache_hierarchy):
        """Test cache miss scenario."""
        # Try to get non-existent key
        value = await cache_hierarchy.get("nonexistent")
        assert value is None
        assert cache_hierarchy.metrics.l1_misses >= 1
        assert cache_hierarchy.metrics.l2_misses >= 1

    @pytest.mark.asyncio
    async def test_hierarchy_set_from_source(self, cache_hierarchy):
        """Test set_from_source method."""
        # Set from source (simulates fetching from API)
        await cache_hierarchy.set_from_source(
            "source_key", "source_value", ttl_seconds=60
        )

        # Verify value is in both caches
        value = await cache_hierarchy.get("source_key")
        assert value == "source_value"
        assert cache_hierarchy.metrics.total_sets == 1

    @pytest.mark.asyncio
    async def test_hierarchy_delete_operations(self, cache_hierarchy):
        """Test delete operations."""
        # Set a value
        await cache_hierarchy.set("delete_key", "delete_value")

        # Verify it exists
        value = await cache_hierarchy.get("delete_key")
        assert value == "delete_value"

        # Delete the key
        result = await cache_hierarchy.delete("delete_key")
        assert result is True

        # Verify it's gone
        value = await cache_hierarchy.get("delete_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_hierarchy_clear_operations(self, cache_hierarchy):
        """Test clear operations."""
        # Add some items
        await cache_hierarchy.set("key1", "value1")
        await cache_hierarchy.set("key2", "value2")
        assert cache_hierarchy.metrics.total_sets == 2

        # Clear all items
        await cache_hierarchy.clear()

        # Verify all items are gone
        assert await cache_hierarchy.get("key1") is None
        assert await cache_hierarchy.get("key2") is None

    @pytest.mark.asyncio
    async def test_hierarchy_metrics_comprehensive(self, cache_hierarchy):
        """Test comprehensive metrics tracking."""
        # Set some values
        await cache_hierarchy.set("metrics_key1", "value1")
        await cache_hierarchy.set("metrics_key2", "value2")

        # Get existing values (L1 hits)
        await cache_hierarchy.get("metrics_key1")
        await cache_hierarchy.get("metrics_key2")

        # Try to get non-existent value (miss)
        await cache_hierarchy.get("nonexistent")

        metrics = cache_hierarchy.get_metrics()

        assert metrics["total_sets"] == 2
        assert metrics["total_gets"] == 3
        assert metrics["l1_hit_ratio"] == 1.0  # 2 hits out of 2 gets
        assert metrics["l1_size"] >= 2
        assert metrics["l2_size"] >= 2
        assert metrics["overall_hit_ratio"] == 2.0 / 3.0  # 2/3

    @pytest.mark.asyncio
    async def test_hierarchy_l1_eviction_with_l2_persistence(self, cache_hierarchy):
        """Test L1 eviction while L2 retains data."""
        # Create small L1 cache
        small_cache = CacheHierarchy(l1_max_size=2, l2_ttl_seconds=30)
        await small_cache.start()

        try:
            # Add 2 items to fill L1
            await small_cache.set("key1", "value1")
            await small_cache.set("key2", "value2")

            # Add 3rd item - should evict L1 key1
            await small_cache.set("key3", "value3")

            # key1 should be gone from L1 but still in L2
            l1_size, l2_size = small_cache.size()
            assert l1_size == 2  # Only key2 and key3 in L1
            assert l2_size == 3  # All keys in L2

            # Getting key1 should hit L2 and populate L1 again
            value = await small_cache.get("key1")
            assert value == "value1"

            # Now key1 should be back in L1
            l1_size, l2_size = small_cache.size()
            assert l1_size == 3  # All keys back in L1 (key1 was added back)

        finally:
            await small_cache.stop()


class TestCacheHierarchyPerformance:
    """Test cache hierarchy performance characteristics."""

    @pytest.mark.asyncio
    async def test_l1_hit_latency(self):
        """Test that L1 hits are very fast (<5ms)."""
        cache = CacheHierarchy(l1_max_size=100)
        await cache.start()

        try:
            # Warm up cache
            await cache.set("perf_key", "perf_value")

            # Measure L1 hit latency
            start_time = time.time()
            for _ in range(100):  # Multiple iterations for stable measurement
                await cache.get("perf_key")
            end_time = time.time()

            avg_latency_ms = (end_time - start_time) / 100 * 1000
            assert avg_latency_ms < 5.0, f"L1 hit latency too high: {avg_latency_ms}ms"

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_l2_hit_slower_than_l1(self):
        """Test that L2 hits are slower than L1 hits."""
        cache = CacheHierarchy(l1_max_size=10)
        await cache.start()

        try:
            # Set value directly to L2 (bypassing L1)
            await cache.l2_cache.set("l2_only_key", "l2_value")

            # First access should hit L2 and populate L1
            l2_start = time.time()
            await cache.get("l2_only_key")
            l2_time = time.time() - l2_start

            # Second access should hit L1 (much faster)
            l1_start = time.time()
            await cache.get("l2_only_key")
            l1_time = time.time() - l1_start

            # L1 should be faster than initial L2 access (at least 2x faster)
            assert l1_time < l2_time * 0.5, (
                f"L1 hit not faster than L2: L1={l1_time * 1000:.3f}ms, L2={l2_time * 1000:.3f}ms"
            )

        finally:
            await cache.stop()


class TestGlobalCacheHierarchy:
    """Test global cache hierarchy instance."""

    @pytest.mark.asyncio
    async def test_get_cache_hierarchy_singleton(self):
        """Test that get_cache_hierarchy returns singleton instance."""
        cache1 = get_cache_hierarchy()
        cache2 = get_cache_hierarchy()

        # Should be the same instance
        assert cache1 is cache2

        # Should be able to use the cache
        await cache1.set("singleton_test", "test_value")
        value = await cache1.get("singleton_test")
        assert value == "test_value"

        # Clean up
        await cache1.stop()


class TestCacheHierarchyIntegration:
    """Integration tests with mocked Redis."""

    @pytest.mark.asyncio
    async def test_hierarchy_with_redis_down(self):
        """Test behavior when Redis (L2) is unavailable."""
        with patch("resync.core.async_cache.AsyncTTLCache") as mock_redis:
            # Mock Redis cache to simulate failure
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = Exception("Redis connection failed")
            mock_instance.set.side_effect = Exception("Redis connection failed")
            mock_redis.return_value = mock_instance

            cache = CacheHierarchy(l1_max_size=10)
            await cache.start()

            try:
                # Should still work with L1 only
                await cache.set("redis_down_key", "redis_down_value")
                value = await cache.get("redis_down_key")
                assert value == "redis_down_value"

                # L1 should still work
                l1_size, l2_size = cache.size()
                assert l1_size >= 1

            finally:
                await cache.stop()


class TestCacheHierarchyStress:
    """Stress tests for cache hierarchy."""

    @pytest.mark.asyncio
    async def test_high_concurrency(self):
        """Test cache hierarchy under high concurrency."""
        cache = CacheHierarchy(l1_max_size=1000)
        await cache.start()

        try:

            async def worker(worker_id: int):
                for i in range(100):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"

                    # Mix of operations
                    await cache.set(key, value)
                    result = await cache.get(key)
                    assert result == value

                    if i % 10 == 0:  # Occasionally delete
                        await cache.delete(key)

                return worker_id

            # Run 10 concurrent workers
            tasks = [worker(i) for i in range(10)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 10
            assert len(set(results)) == 10  # All workers completed

            # Cache should be populated
            l1_size, l2_size = cache.size()
            assert l1_size > 0
            assert l2_size > 0

        finally:
            await cache.stop()
