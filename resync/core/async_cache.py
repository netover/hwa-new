from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import time
from typing import Any, Dict, List, Optional, Tuple

from resync.core.exceptions import CacheError

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single entry in the cache with timestamp and TTL."""

    data: Any
    timestamp: float
    ttl: float


class AsyncTTLCache:
    """
    A truly asynchronous TTL cache that eliminates blocking I/O.

    Features:
    - Async get() and set() methods for non-blocking operations
    - Thread-safe concurrent access using sharded asyncio.Lock
    - Background cleanup task for expired entries
    - Time-based eviction using asyncio.sleep()
    """

    def __init__(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30, num_shards: int = 16
    ):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
            num_shards: Number of shards for the lock
        """
        # Read TTL and cleanup interval from configuration, if available
        # Assuming get_config() reads from config.yaml
        try:
            from your_config_module import get_config  # Replace your_config_module

            config = get_config()
            self.ttl_seconds = config.get("async_cache", {}).get(
                "ttl_seconds", ttl_seconds
            )
            self.cleanup_interval = config.get("async_cache", {}).get(
                "cleanup_interval", cleanup_interval
            )
        except ImportError:
            # Handle the case where your_config_module is not available
            self.ttl_seconds = ttl_seconds
            self.cleanup_interval = cleanup_interval

        self.num_shards = num_shards
        self.shards: List[Dict[str, CacheEntry]] = [{} for _ in range(num_shards)]
        self.shard_locks = [asyncio.Lock() for _ in range(num_shards)]
        self.cleanup_task: Optional[asyncio.Task[None]] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def _get_shard(self, key: str) -> Tuple[Dict[str, CacheEntry], asyncio.Lock]:
        """Get the shard and lock for a given key."""
        shard_index = hash(key) % self.num_shards
        return self.shards[shard_index], self.shard_locks[shard_index]

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    async def _cleanup_expired_entries(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("AsyncTTLCache cleanup task cancelled")
                break
            except MemoryError as e:
                logger.error("Memory error in AsyncTTLCache cleanup task: %s", e)
                raise CacheError("Memory error during cache cleanup") from e
            except KeyError as e:
                logger.error("Key error in AsyncTTLCache cleanup task: %s", e)
                raise CacheError(f"Key error during cache cleanup: {e}") from e
            except RuntimeError as e:
                logger.error("Runtime error in AsyncTTLCache cleanup task: %s", e)
                raise CacheError(f"Runtime error during cache cleanup: {e}") from e
            except Exception as e:
                logger.error("Unexpected error in AsyncTTLCache cleanup task: %s", e)
                raise CacheError(f"Unexpected error during cache cleanup: {e}") from e

    async def _remove_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        total_removed = 0
        for i in range(self.num_shards):
            shard = self.shards[i]
            lock = self.shard_locks[i]
            async with lock:
                expired_keys = [
                    key
                    for key, entry in shard.items()
                    if current_time - entry.timestamp > entry.ttl
                ]
                for key in expired_keys:
                    del shard[key]
                    logger.debug("Removed expired cache entry: %s", key)
                total_removed += len(expired_keys)

        if total_removed > 0:
            logger.debug("Cleaned up %d expired cache entries", total_removed)

    async def get(self, key: str) -> Any | None:
        """
        Asynchronously retrieve an item from the cache.

        Args:
            key: Cache key to retrieve
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        shard, lock = self._get_shard(key)
        async with lock:
            entry = shard.get(key)
            if entry:
                current_time = time()
                if current_time - entry.timestamp <= entry.ttl:
                    logger.debug("Cache HIT for key: %s", key)
                    return entry.data
                else:
                    # Entry expired, remove it
                    del shard[key]
                    logger.debug("Cache EXPIRED for key: %s", key)

            logger.debug("Cache MISS for key: %s", key)
            return None

    async def set(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Asynchronously add an item to the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override for this specific entry
        """
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds

        current_time = time()
        entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)

        shard, lock = self._get_shard(key)
        async with lock:
            shard[key] = entry
            logger.debug("Cache SET for key: %s", key)

    async def delete(self, key: str) -> bool:
        """
        Asynchronously delete an item from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        shard, lock = self._get_shard(key)
        async with lock:
            if key in shard:
                del shard[key]
                logger.debug("Cache DELETE for key: %s", key)
                return True
            return False

    async def clear(self) -> None:
        """Asynchronously clear all cache entries."""
        for i in range(self.num_shards):
            shard = self.shards[i]
            lock = self.shard_locks[i]
            async with lock:
                shard.clear()
        logger.debug("Cache CLEARED")

    def size(self) -> int:
        """Get the current number of items in cache (non-async for performance)."""
        return sum(len(shard) for shard in self.shards)

    async def stop(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def __aenter__(self) -> "AsyncTTLCache":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup resources."""
        await self.stop()
