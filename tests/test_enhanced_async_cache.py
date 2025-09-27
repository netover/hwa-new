import asyncio
import time
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from resync.core.enhanced_async_cache import EnhancedAsyncTTLCache, ConsistentHash


class TestConsistentHash:
    """Test suite for ConsistentHash functionality."""

    def test_consistent_distribution(self):
        """Test that keys are distributed evenly across shards."""
        num_shards = 16
        hasher = ConsistentHash(num_shards=num_shards)

        # Generate a large number of keys
        keys = [f"test_key_{i}" for i in range(10000)]

        # Count distribution
        distribution = [0] * num_shards
        for key in keys:
            shard_id = hasher.get_shard(key)
            distribution[shard_id] += 1

        # Check that no shard is empty and distribution is relatively even
        for count in distribution:
            assert count > 0

        # Standard deviation should be relatively low for even distribution
        mean = sum(distribution) / len(distribution)
        variance = sum((x - mean) ** 2 for x in distribution) / len(distribution)
        std_dev = variance**0.5

        # Standard deviation should be less than 10% of mean for good distribution
        assert std_dev < mean * 0.1

    def test_consistent_after_changes(self):
        """Test that most keys stay on the same shard when number of shards changes."""
        # Start with 16 shards
        hasher_16 = ConsistentHash(num_shards=16)

        # Generate test keys
        keys = [f"test_key_{i}" for i in range(1000)]

        # Get initial mapping
        initial_mapping = {key: hasher_16.get_shard(key) for key in keys}

        # Create new hasher with 20 shards
        hasher_20 = ConsistentHash(num_shards=20)

        # Get new mapping
        new_mapping = {key: hasher_20.get_shard(key % 20) for key in keys}

        # Count how many keys changed shards
        changed = sum(
            1 for key in keys if new_mapping.get(key) != initial_mapping.get(key)
        )

        # With consistent hashing, only about 20% of keys should change
        # (proportional to the change in number of shards)
        assert changed < len(keys) * 0.3


class TestEnhancedAsyncTTLCache:
    """Test suite for EnhancedAsyncTTLCache functionality."""

    @pytest_asyncio.fixture
    async def cache(self):
        """Create a cache instance for testing."""
        cache = EnhancedAsyncTTLCache(ttl_seconds=1, cleanup_interval=0.1)
        yield cache
        await cache.stop()

    @pytest.mark.asyncio
    async def test_basic_get_set(self, cache):
        """Test basic get/set operations."""
        # Test set operation
        await cache.set("test_key", "test_value")
        assert cache.size() == 1

        # Test get operation
        value = await cache.get("test_key")
        assert value == "test_value"

        # Test get non-existent key
        value = await cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL-based expiration."""
        # Set a value with short TTL
        await cache.set("ttl_key", "ttl_value", ttl_seconds=0.5)

        # Should be available immediately
        value = await cache.get("ttl_key")
        assert value == "ttl_value"

        # Wait for expiration
        await asyncio.sleep(0.6)

        # Should be None after expiration
        value = await cache.get("ttl_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete_operation(self, cache):
        """Test delete operation."""
        # Set and verify value exists
        await cache.set("delete_key", "delete_value")
        value = await cache.get("delete_key")
        assert value == "delete_value"

        # Delete and verify it's gone
        result = await cache.delete("delete_key")
        assert result is True
        assert cache.size() == 0

        # Verify get returns None
        value = await cache.get("delete_key")
        assert value is None

        # Test deleting non-existent key
        result = await cache.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_operation(self, cache):
        """Test clear operation."""
        # Add multiple items
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        assert cache.size() == 3

        # Clear all items
        await cache.clear()
        assert cache.size() == 0

        # Verify all items are gone
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
        assert await cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache):
        """Test thread-safe concurrent access with hierarchical locking."""

        async def set_multiple_times(key, value, times):
            """Set the same key multiple times concurrently."""
            for i in range(times):
                await cache.set(key, f"{value}_{i}")
                await asyncio.sleep(0.01)  # Small delay to allow interleaving

        async def get_multiple_times(key, times):
            """Get the same key multiple times concurrently."""
            results = []
            for _ in range(times):
                value = await cache.get(key)
                results.append(value)
                await asyncio.sleep(0.01)
            return results

        # Test concurrent sets
        await asyncio.gather(
            set_multiple_times("concurrent_key", "value", 10),
            set_multiple_times("concurrent_key", "value", 10),
            set_multiple_times("concurrent_key", "value", 10),
        )

        # Test concurrent gets
        results = await asyncio.gather(
            get_multiple_times("concurrent_key", 5),
            get_multiple_times("concurrent_key", 5),
            get_multiple_times("concurrent_key", 5),
        )

        # All results should be the same (last set value)
        expected_value = "value_9"  # Last value set
        for result_list in results:
            assert all(value == expected_value for value in result_list)

    @pytest.mark.asyncio
    async def test_parallel_cleanup(self):
        """Test parallel cleanup of expired entries."""
        cache = EnhancedAsyncTTLCache(ttl_seconds=0.2, cleanup_interval=0.1)

        try:
            # Add many items with short TTL
            for i in range(100):
                await cache.set(f"short_ttl_{i}", f"value_{i}", ttl_seconds=0.1)

            # Add some items with longer TTL
            for i in range(50):
                await cache.set(f"long_ttl_{i}", f"long_value_{i}", ttl_seconds=1)

            # Verify initial count
            assert cache.size() == 150

            # Wait for short TTL to expire and cleanup to run
            time.time()
            await asyncio.sleep(0.3)

            # Short TTL items should be gone, long TTL should remain
            assert cache.size() <= 50  # Should be around 50 (long TTL items)

            # Get metrics to verify cleanup happened
            metrics = cache.get_metrics()
            assert metrics["expired"] >= 100  # At least 100 items expired

            # Check cleanup duration is reasonable (should be faster with parallel cleanup)
            assert metrics["cleanup_duration_ms"] > 0

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_optimistic_read(self, cache):
        """Test optimistic read for high-read scenarios."""
        # Set up a value
        await cache.set("optimistic_key", "optimistic_value")

        # Mock the shard.get method to track if it's called
        original_get = cache._get_shard("optimistic_key").get
        mock_get = MagicMock(side_effect=original_get)
        cache._get_shard("optimistic_key").get = mock_get

        # First get should use optimistic read and not call shard.get
        value = await cache.get("optimistic_key")
        assert value == "optimistic_value"
        mock_get.assert_not_called()

        # For a non-existent key, should fall back to shard.get
        value = await cache.get("nonexistent_key")
        assert value is None

        # Restore original method
        cache._get_shard("optimistic_key").get = original_get

    @pytest.mark.asyncio
    async def test_metrics_collection(self, cache):
        """Test that metrics are properly collected."""
        # Perform various operations
        await cache.set("metrics_key1", "value1")
        await cache.get("metrics_key1")
        await cache.get("nonexistent_key")
        await cache.set("metrics_key2", "value2")
        await cache.delete("metrics_key1")

        # Get metrics
        metrics = cache.get_metrics()

        # Verify metrics are tracked
        assert metrics["gets"] == 2
        assert metrics["hits"] == 1
        assert metrics["misses"] == 1
        assert metrics["sets"] == 2
        assert metrics["deletes"] == 1
        assert metrics["size"] == 1

        # Hit ratio should be 0.5 (1 hit, 1 miss)
        assert metrics["hit_ratio"] == 0.5

    @pytest.mark.asyncio
    async def test_high_concurrency_stress(self, cache):
        """Test cache under high concurrency stress (100+ operations)."""

        async def stress_worker(worker_id):
            """Worker function for stress testing."""
            for i in range(50):
                key = f"stress_key_{worker_id}_{i}"
                value = f"stress_value_{worker_id}_{i}"

                # Set value
                await cache.set(key, value)
                assert cache.size() >= 0  # Size should always be non-negative

                # Get value
                retrieved = await cache.get(key)
                assert retrieved == value

                # Randomly delete some entries
                if i % 10 == 0:
                    await cache.delete(key)
                    assert cache.size() >= 0

        # Run 5 concurrent workers, each doing 50 operations
        await asyncio.gather(*[stress_worker(i) for i in range(5)])

        # Cache should still be functional after stress test
        await cache.set("final_test", "final_value")
        assert await cache.get("final_test") == "final_value"

        # Check metrics after stress test
        metrics = cache.get_metrics()
        assert metrics["gets"] > 0
        assert metrics["sets"] > 0
