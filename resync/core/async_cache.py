from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import time
from typing import Any, Dict, Optional

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
    - Thread-safe concurrent access using asyncio.Lock
    - Background cleanup task for expired entries
    - Time-based eviction using asyncio.sleep()
    """

    def __init__(self, ttl_seconds: int = 60, cleanup_interval: int = 30):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = asyncio.Lock()
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

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
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def _remove_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        expired_keys = []

        # Find expired entries without holding the lock
        for key, entry in self.cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)

        # Remove expired entries while holding the lock
        if expired_keys:
            async with self.lock:
                for key in expired_keys:
                    if key in self.cache:
                        del self.cache[key]
                        logger.debug(f"Removed expired cache entry: {key}")

                if expired_keys:
                    logger.debug(
                        f"Cleaned up {len(expired_keys)} expired cache entries"
                    )

    async def get(self, key: str) -> Any | None:
        """
        Asynchronously retrieve an item from the cache.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            entry = self.cache.get(key)
            if entry:
                current_time = time()
                if current_time - entry.timestamp <= entry.ttl:
                    logger.debug(f"Cache HIT for key: {key}")
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")

            logger.debug(f"Cache MISS for key: {key}")
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

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def delete(self, key: str) -> bool:
        """
        Asynchronously delete an item from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Cache DELETE for key: {key}")
                return True
            return False

    async def clear(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug("Cache CLEARED")

    def size(self) -> int:
        """Get the current number of items in cache (non-async for performance)."""
        return len(self.cache)

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

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.stop()
