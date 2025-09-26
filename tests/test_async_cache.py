import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio

from resync.core.async_cache import AsyncTTLCache


class TestAsyncTTLCache:
    """Test suite for AsyncTTLCache functionality."""

    @pytest_asyncio.fixture
    async def cache(self):
        """Create a cache instance for testing."""
        cache = AsyncTTLCache(ttl_seconds=1, cleanup_interval=0.1)
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
        """Test thread-safe concurrent access."""

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
    async def test_background_cleanup(self):
        """Test background cleanup task."""
        cache = AsyncTTLCache(ttl_seconds=0.2, cleanup_interval=0.1)

        try:
            # Add items with different TTLs
            await cache.set("short_ttl", "short", ttl_seconds=0.1)
            await cache.set("long_ttl", "long", ttl_seconds=1)

            # Verify both exist initially
            assert await cache.get("short_ttl") == "short"
            assert await cache.get("long_ttl") == "long"
            assert cache.size() == 2

            # Wait for short TTL to expire and cleanup to run
            await asyncio.sleep(0.3)

            # Short TTL should be gone, long TTL should remain
            assert await cache.get("short_ttl") is None
            assert await cache.get("long_ttl") == "long"
            assert cache.size() == 1

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        async with AsyncTTLCache(ttl_seconds=1) as cache:
            # Test that cache works within context
            await cache.set("context_key", "context_value")
            value = await cache.get("context_key")
            assert value == "context_value"

        # After exiting context, cache should be stopped
        # We can't easily test the stopped state, but the context exit should work

    @pytest.mark.asyncio
    async def test_custom_ttl_per_entry(self, cache):
        """Test setting different TTL for individual entries."""
        # Set entries with different TTLs
        await cache.set("short", "short_value", ttl_seconds=0.1)
        await cache.set("long", "long_value", ttl_seconds=2)

        # Both should be available initially
        assert await cache.get("short") == "short_value"
        assert await cache.get("long") == "long_value"

        # Wait for short to expire
        await asyncio.sleep(0.2)

        # Short should be gone, long should remain
        assert await cache.get("short") is None
        assert await cache.get("long") == "long_value"

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

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, cache):
        """Test that expired entries don't accumulate in memory."""
        # Add many entries
        for i in range(100):
            await cache.set(f"memory_key_{i}", f"value_{i}", ttl_seconds=0.1)

        assert cache.size() == 100

        # Wait for cleanup
        await asyncio.sleep(0.2)

        # Should have fewer entries due to cleanup
        final_size = cache.size()
        assert final_size < 100  # Some entries should have been cleaned up

        # Add new entries to ensure cache still works
        await cache.set("new_key", "new_value")
        assert await cache.get("new_key") == "new_value"

    @pytest.mark.asyncio
    async def test_cache_stop_behavior(self):
        """Test that cache stops correctly."""
        cache = AsyncTTLCache(ttl_seconds=1)

        # Verify cache is running
        assert cache.is_running is True

        # Stop the cache
        await cache.stop()

        # Verify cache is stopped
        assert cache.is_running is False
        assert cache.cleanup_task is None or cache.cleanup_task.done()


# Integration test with the TWS client
class TestAsyncTTLCacheIntegration:
    """Integration tests with OptimizedTWSClient."""

    @pytest.mark.asyncio
    async def test_tws_client_cache_integration(self):
        """Test that TWS client properly uses AsyncTTLCache."""
        from resync.services.tws_service import OptimizedTWSClient
        from resync.settings import settings

        # Mock the settings to avoid needing real TWS credentials
        with patch.object(settings, "TWS_CACHE_TTL", 60):
            client = OptimizedTWSClient(
                hostname="localhost",
                port=31116,
                username="test",
                password="test",
            )

            # Verify cache is properly initialized
            from resync.core.cache_hierarchy import CacheHierarchy

            assert isinstance(client.cache, CacheHierarchy)

            # Test cache operations work
            await client.cache.set("test", "test_value")
            result = await client.cache.get("test")
            assert result == "test_value"

            # Test cache cleanup on close
            await client.close()

            # Verify cache is stopped after close
            assert client.cache.is_running is False
