from __future__ import annotations

import asyncio
import logging
from collections import OrderedDict
from dataclasses import dataclass
from time import time as time_func
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import Counter, Histogram

from resync.core.enhanced_async_cache import TWS_OptimizedAsyncCache
from resync.settings import settings

cache_hits = Counter('cache_hierarchy_hits_total', 'Total cache hits', ['cache_level'])
cache_misses = Counter('cache_hierarchy_misses_total', 'Total cache misses', ['cache_level'])
cache_latency = Histogram('cache_hierarchy_latency_seconds', 'Cache operation latency', ['cache_level'])

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Tracks cache performance metrics."""

    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    total_gets: int = 0
    total_sets: int = 0
    l1_evictions: int = 0
    l1_get_latency: float = 0.0
    l2_get_latency: float = 0.0
    miss_latency: float = 0.0

    @property
    def l1_hit_ratio(self) -> float:
        """Calculate L1 hit ratio."""
        total = self.l1_hits + self.l1_misses
        return self.l1_hits / total if total > 0 else 0.0

    @property
    def l2_hit_ratio(self) -> float:
        """Calculate L2 hit ratio."""
        total = self.l2_hits + self.l2_misses
        return self.l2_hits / total if total > 0 else 0.0

    @property
    def overall_hit_ratio(self) -> float:
        """Calculate overall hit ratio."""
        total = self.total_gets
        hits = self.l1_hits + self.l2_hits
        return hits / total if total > 0 else 0.0


class L1Cache:
    """
    In-memory L1 cache with LRU eviction and sharded asyncio.Lock protection.
    """

    def __init__(self, max_size: int = 1000, num_shards: int = 16):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
            num_shards: Number of shards for the cache and locks
        """
        if num_shards <= 0:
            raise ValueError("num_shards must be a positive integer")

        self.max_size = max_size
        self.num_shards = num_shards
        self.shards: List[OrderedDict[str, Tuple[Any, float]]] = [
            OrderedDict() for _ in range(num_shards)
        ]
        self.shard_locks = [asyncio.Lock() for _ in range(num_shards)]
        self.shard_max_size = max_size // num_shards if num_shards > 0 else max_size

    def _get_shard(
        self, key: str
    ) -> Tuple[OrderedDict[str, Tuple[Any, float]], asyncio.Lock]:
        """Get the shard and lock for a given key."""
        shard_index = hash(key) % self.num_shards
        return self.shards[shard_index], self.shard_locks[shard_index]

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        shard, lock = self._get_shard(key)
        async with lock:
            if key in shard:
                value, timestamp = shard[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                shard.move_to_end(key)  # Move to most recently used
                logger.debug("L1 cache HIT for key: %s", key)
                return value

            logger.debug("L1 cache MISS for key: %s", key)
            return None

    async def set(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        shard, lock = self._get_shard(key)
        async with lock:
            current_time = time_func()

            # Add or update entry
            shard[key] = (value, current_time)
            shard.move_to_end(key)  # Move to most recently used

            # Check if we need to evict - check total cache size
            current_total_size = sum(len(s) for s in self.shards)
            if self.max_size > 0 and current_total_size > self.max_size:
                # Find and evict LRU item from any shard
                for s in self.shards:
                    if s:
                        evicted_key, _ = s.popitem(last=False)  # Remove LRU
                        logger.debug("L1 cache EVICTION for key: %s", evicted_key)
                        break

    async def delete(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        shard, lock = self._get_shard(key)
        async with lock:
            if key in shard:
                del shard[key]
                logger.debug("L1 cache DELETE for key: %s", key)
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries from L1 cache."""
        for i in range(self.num_shards):
            shard = self.shards[i]
            lock = self.shard_locks[i]
            async with lock:
                shard.clear()
        logger.debug("L1 cache CLEARED")

    def size(self) -> int:
        """Get current size of L1 cache."""
        return sum(len(shard) for shard in self.shards)


class CacheHierarchy:
    """
    Two-tier cache hierarchy with L1 (in-memory) and L2 (Redis-backed).

    Priority: L1 read → if miss → L2 read → if miss → fetch from source → write to L2 → write to L1
    Write-through: All writes go to L2 first, then L1
    """

    def __init__(
        self,
        l1_max_size: int = 1000,
        l2_ttl_seconds: int = 300,
        l2_cleanup_interval: int = 30,
    ):
        """
        Initialize cache hierarchy.

        Args:
            l1_max_size: Maximum entries in L1 cache before LRU eviction
            l2_ttl_seconds: TTL for L2 cache entries
            l2_cleanup_interval: Cleanup interval for L2 cache
        """
        # Use settings from the project configuration
        from resync.settings import settings

        self.l1_cache = L1Cache(max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE, num_shards=settings.CACHE_HIERARCHY_NUM_SHARDS)
        self.l2_cache = TWS_OptimizedAsyncCache(
            ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
            num_shards=settings.CACHE_HIERARCHY_NUM_SHARDS,
            max_workers=settings.CACHE_HIERARCHY_MAX_WORKERS,
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    async def start(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info("CacheHierarchy started")

    async def stop(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info("CacheHierarchy stopped")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        if len(key) > 256:
            logger.warning(f"Cache key too long: {len(key)} chars, truncating")
            key = key[:256]  # Truncate to prevent memory issues

        start_time = time_func()
        self.metrics.total_gets += 1

        try:
            # Try L1 first (fastest)
            l1_start = time_func()
            l1_value = await self.l1_cache.get(key)
            l1_latency = time_func() - l1_start # Re-introduce L1 latency calculation
            self.metrics.l1_get_latency = (self.metrics.l1_get_latency + l1_latency) / 2 # Update internal metric

            if l1_value is not None:
                self.metrics.l1_hits += 1
                cache_hits.labels(cache_level='l1').inc()
                # Ensure l1_latency is defined here
                cache_latency.labels(cache_level='l1').observe(l1_latency)
                logger.debug(
                    f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
                )
                return l1_value
            self.metrics.l1_misses += 1

            # Try L2 if L1 miss
            l2_start = time_func()
            l2_value = await self.l2_cache.get(key)
            l2_latency = time_func() - l2_start # This one was already here
            self.metrics.l2_get_latency = (self.metrics.l2_get_latency + l2_latency) / 2 # Update internal metric
            
            if l2_value is not None:
                self.metrics.l2_hits += 1
                cache_hits.labels(cache_level='l2').inc()
                cache_latency.labels(cache_level='l2').observe(l2_latency) # Observe L2 latency
                # Simplified: Always write L2 value to L1 without complex double-check
                # This trades perfect consistency for simplicity and performance
                await self.l1_cache.set(key, l2_value)
                logger.debug(
                    f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
                )
                return l2_value

            self.metrics.l2_misses += 1
            cache_misses.labels(cache_level='l2').inc()
            miss_latency = time_func() - start_time # This one was already here
            self.metrics.miss_latency = (self.metrics.miss_latency + miss_latency) / 2 # Update internal metric

            logger.debug(
                f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
            )
            return None

        except asyncio.TimeoutError:
            logger.warning(f"Cache get operation timed out for key: {key}")
            return None
        except asyncio.CancelledError:
            logger.debug(f"Cache get operation cancelled for key: {key}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in cache get for key {key}: {e}", exc_info=True
            )
            return None

    async def set(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        if len(key) > 256:
            logger.warning(f"Cache key too long: {len(key)} chars, truncating for set operation")
            key = key[:256] # Truncate for set operations as well

        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)
        self.metrics.l1_evictions += 1

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def set_from_source(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        if len(key) > 256:
            logger.warning(f"Cache key too long: {len(key)} chars, truncating for set_from_source operation")
            key = key[:256] # Truncate for set_from_source operations as well

        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)
        self.metrics.l1_evictions += 1

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def delete(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        if len(key) > 256:
            logger.warning(f"Cache key too long: {len(key)} chars, truncating for delete operation")
            key = key[:256] # Truncate for delete operations as well

        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def clear(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug("Cache HIERARCHY CLEARED")

    def size(self) -> Tuple[int, int]:
        """Get sizes of both cache tiers."""
        l1_size = self.l1_cache.size()
        # Note: l2_cache.size() is async, but we keep sync signature for compatibility
        # For now, return a tuple with async placeholder
        return l1_size, 0  # TODO: Make this async or handle differently

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    async def __aenter__(self) -> "CacheHierarchy":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()


# Global cache hierarchy instance
cache_hierarchy: Optional[CacheHierarchy] = None


def get_cache_hierarchy() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy