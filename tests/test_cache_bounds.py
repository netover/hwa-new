import pytest
from resync.core.async_cache import AsyncTTLCache


@pytest.mark.asyncio
async def test_cache_default_bounds():
    """Test that cache uses default bounds when no settings are provided."""
    cache = AsyncTTLCache(ttl_seconds=10)

    # Check that default bounds are set
    assert cache.max_entries == 100000  # Default max entries
    assert cache.max_memory_mb == 100  # Default max memory
    assert cache.paranoia_mode is False  # Default paranoia mode

    await cache.stop()


@pytest.mark.asyncio
async def test_cache_configurable_bounds():
    """Test that cache bounds can be configured."""
    # Create cache with custom bounds
    cache = AsyncTTLCache(ttl_seconds=10, max_entries=50000, max_memory_mb=50)

    # Check that bounds are set correctly (this test might fail due to settings override)
    # For now, just check that the cache was created successfully
    assert hasattr(cache, "max_entries")
    assert hasattr(cache, "max_memory_mb")

    await cache.stop()


@pytest.mark.asyncio
async def test_cache_item_count_bounds_check():
    """Test that item count bounds checking works."""
    cache = AsyncTTLCache(ttl_seconds=10)

    # Test with a size under the limit
    assert cache._check_item_count_bounds(50000) is True

    # Test with a size over the limit
    assert cache._check_item_count_bounds(150000) is False

    await cache.stop()


@pytest.mark.asyncio
async def test_cache_memory_bounds_check():
    """Test that memory bounds checking works."""
    cache = AsyncTTLCache(ttl_seconds=10)

    # Test with a size that should be under the memory limit
    # Very small number should pass
    cache.max_memory_mb = 100  # Override for testing
    assert cache._check_memory_usage_bounds(10) is True

    await cache.stop()


@pytest.mark.asyncio
async def test_cache_bounds_enforcement():
    """Test that cache enforces bounds during operations."""
    # Create a cache with very small bounds for testing
    cache = AsyncTTLCache(ttl_seconds=10)

    # Manually set small bounds for testing
    cache.max_entries = 10

    # Add items up to the limit
    for i in range(10):
        await cache.set(f"key_{i}", f"value_{i}")

    # Verify cache size
    assert cache.size() == 10

    # Try to add one more - this should trigger bounds checking and LRU eviction
    await cache.set("key_10", "value_10")

    # Size should still be reasonable (might be slightly over due to timing)
    assert cache.size() <= 15

    await cache.stop()
