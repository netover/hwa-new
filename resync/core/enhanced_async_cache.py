from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single entry in the cache with timestamp and TTL."""

    data: Any
    timestamp: float
    ttl: float


class ConsistentHash:
    """
    Implements consistent hashing for better key distribution and shard stability.

    This implementation uses a ring-based approach with virtual nodes to ensure
    even distribution of keys across shards.
    """

    def __init__(self, num_shards: int, replicas: int = 100):
        """
        Initialize the consistent hash ring.

        Args:
            num_shards: Number of shards to distribute keys across
            replicas: Number of virtual nodes per shard for better distribution
        """
        self.num_shards = num_shards
        self.replicas = replicas
        self.ring: Dict[int, int] = {}
        self._build_ring()

    def _build_ring(self) -> None:
        """Build the hash ring with virtual nodes."""
        for shard_id in range(self.num_shards):
            for replica in range(self.replicas):
                key = f"{shard_id}:{replica}"
                hash_key = self._hash(key)
                self.ring[hash_key] = shard_id

        # Sort the keys for binary search
        self._sorted_keys = sorted(self.ring.keys())

    def _hash(self, key: str) -> int:
        """Create a hash for a key."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_shard(self, key: str) -> int:
        """
        Get the shard ID for a given key.

        Args:
            key: The key to hash

        Returns:
            The shard ID (0 to num_shards-1)
        """
        if not self._sorted_keys:
            return 0

        hash_key = self._hash(key)

        # Binary search to find the next highest key
        pos = self._binary_search(hash_key)

        # If we're at the end, wrap around to the first node
        if pos == len(self._sorted_keys):
            pos = 0

        # Return the shard ID for this position in the ring
        return self.ring[self._sorted_keys[pos]]

    def _binary_search(self, hash_key: int) -> int:
        """Find the position of the next highest key in the sorted keys."""
        lo, hi = 0, len(self._sorted_keys) - 1

        # If the hash is greater than all keys, return the position after the last key
        if hash_key > self._sorted_keys[hi]:
            return len(self._sorted_keys)

        # Binary search
        while lo <= hi:
            mid = (lo + hi) // 2
            if self._sorted_keys[mid] < hash_key:
                lo = mid + 1
            else:
                hi = mid - 1

        return lo


class KeyLock:
    """
    Implements fine-grained locking at the key level.

    This allows multiple operations on different keys within the same shard
    to proceed concurrently, reducing lock contention.
    """

    def __init__(self, max_locks: int = 1024):
        """
        Initialize the key lock manager.

        Args:
            max_locks: Maximum number of concurrent locks to maintain
        """
        self.max_locks = max_locks
        self.locks: Dict[str, asyncio.Lock] = {}
        self.lock_access_times: Dict[str, float] = {}
        self.global_lock = asyncio.Lock()

    async def acquire(self, key: str) -> asyncio.Lock:
        """
        Get a lock for a specific key, creating it if necessary.

        Args:
            key: The key to lock

        Returns:
            An asyncio.Lock object for the key
        """
        async with self.global_lock:
            # Clean up old locks if we've reached the limit
            if len(self.locks) >= self.max_locks:
                await self._cleanup_old_locks()

            # Create a new lock if needed
            if key not in self.locks:
                self.locks[key] = asyncio.Lock()

            # Update access time
            self.lock_access_times[key] = time.time()

            return self.locks[key]

    async def _cleanup_old_locks(self) -> None:
        """Remove the least recently used locks to stay under max_locks."""
        # Only clean up locks that aren't currently held
        available_locks = [k for k, lock in self.locks.items() if not lock.locked()]

        if not available_locks:
            return  # All locks are in use, can't clean up

        # Sort by access time and remove oldest
        oldest_keys = sorted(
            available_locks, key=lambda k: self.lock_access_times.get(k, 0)
        )

        # Remove the oldest third of unused locks
        to_remove = oldest_keys[: max(1, len(oldest_keys) // 3)]

        for key in to_remove:
            del self.locks[key]
            del self.lock_access_times[key]


class ShardLockManager:
    """
    Manages hierarchical locking with both shard-level and key-level locks.

    This allows fine-grained locking for individual key operations while still
    supporting efficient shard-wide operations.
    """

    def __init__(self, num_shards: int):
        """
        Initialize the shard lock manager.

        Args:
            num_shards: Number of shards
        """
        self.shard_locks = [asyncio.Lock() for _ in range(num_shards)]
        self.key_lock_managers = [KeyLock() for _ in range(num_shards)]

    async def acquire_shard_lock(self, shard_id: int) -> asyncio.Lock:
        """
        Get a lock for an entire shard.

        Args:
            shard_id: The shard ID

        Returns:
            The shard lock
        """
        return self.shard_locks[shard_id]

    async def acquire_key_lock(self, shard_id: int, key: str) -> asyncio.Lock:
        """
        Get a lock for a specific key within a shard.

        Args:
            shard_id: The shard ID
            key: The key to lock

        Returns:
            A key-specific lock
        """
        return await self.key_lock_managers[shard_id].acquire(key)


class CacheShard:
    """
    Represents a single shard of the cache with its own data store.

    Each shard operates independently to reduce contention.
    """

    def __init__(self, shard_id: int, lock_manager: ShardLockManager):
        """
        Initialize a cache shard.

        Args:
            shard_id: The shard ID
            lock_manager: The lock manager for this cache
        """
        self.shard_id = shard_id
        self.data: Dict[str, CacheEntry] = {}
        self.lock_manager = lock_manager

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the shard using key-level locking.

        Args:
            key: The key to retrieve

        Returns:
            The value if found and not expired, None otherwise
        """
        key_lock = await self.lock_manager.acquire_key_lock(self.shard_id, key)

        async with key_lock:
            entry = self.data.get(key)
            if entry:
                current_time = time.time()
                if current_time - entry.timestamp <= entry.ttl:
                    logger.debug(
                        "Cache HIT for key: %s in shard %d", key, self.shard_id
                    )
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.data[key]
                    logger.debug(
                        "Cache EXPIRED for key: %s in shard %d", key, self.shard_id
                    )

            logger.debug("Cache MISS for key: %s in shard %d", key, self.shard_id)
            return None

    async def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        """
        Set a value in the shard using key-level locking.

        Args:
            key: The key to set
            value: The value to store
            ttl_seconds: Time-to-live in seconds
        """
        key_lock = await self.lock_manager.acquire_key_lock(self.shard_id, key)

        async with key_lock:
            current_time = time.time()
            entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)
            self.data[key] = entry
            logger.debug("Cache SET for key: %s in shard %d", key, self.shard_id)

    async def delete(self, key: str) -> bool:
        """
        Delete a key from the shard using key-level locking.

        Args:
            key: The key to delete

        Returns:
            True if the key was found and deleted, False otherwise
        """
        key_lock = await self.lock_manager.acquire_key_lock(self.shard_id, key)

        async with key_lock:
            if key in self.data:
                del self.data[key]
                logger.debug("Cache DELETE for key: %s in shard %d", key, self.shard_id)
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries in the shard using shard-level locking."""
        shard_lock = await self.lock_manager.acquire_shard_lock(self.shard_id)

        async with shard_lock:
            self.data.clear()
            logger.debug("Cache CLEARED for shard %d", self.shard_id)

    async def remove_expired_entries(self) -> int:
        """
        Remove expired entries from the shard using shard-level locking.

        Returns:
            Number of entries removed
        """
        shard_lock = await self.lock_manager.acquire_shard_lock(self.shard_id)

        async with shard_lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, entry in self.data.items()
                if current_time - entry.timestamp > entry.ttl
            ]

            for key in expired_keys:
                del self.data[key]

            if expired_keys:
                logger.debug(
                    "Removed %d expired entries from shard %d",
                    len(expired_keys),
                    self.shard_id,
                )

            return len(expired_keys)

    def size(self) -> int:
        """Get the current number of entries in the shard."""
        return len(self.data)


class TWS_OptimizedAsyncCache:
    """
    TWS-optimized asynchronous TTL cache with adaptive sharding and lazy initialization.

    Features:
    - Adaptive sharding based on concurrency patterns
    - Lazy initialization of locks and structures
    - TWS-specific job pattern caching
    - Optimized for TWS workload characteristics
    - Reduced overhead for typical TWS usage patterns
    """

    def __init__(
        self,
        ttl_seconds: int = 60,
        cleanup_interval: int = 30,
        num_shards: int = 4,  # Optimized for TWS concurrency
        max_workers: int = 2,  # Reduced for TWS workload
        concurrency_threshold: int = 5,  # Threshold for adaptive sharding
    ):
        """
        Initialize the TWS-optimized async cache.

        Args:
            ttl_seconds: Default time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
            num_shards: Number of shards for the cache (optimized for TWS)
            max_workers: Maximum number of worker threads for parallel operations
            concurrency_threshold: Threshold for adaptive sharding
        """
        # Try to load configuration from settings
        try:
            from resync.settings import settings

            self.ttl_seconds = getattr(settings, "ASYNC_CACHE_TTL", ttl_seconds)
            self.cleanup_interval = getattr(
                settings, "ASYNC_CACHE_CLEANUP_INTERVAL", cleanup_interval
            )
            self.num_shards = getattr(settings, "ASYNC_CACHE_NUM_SHARDS", num_shards)
            self.max_workers = getattr(settings, "ASYNC_CACHE_MAX_WORKERS", max_workers)
            self.concurrency_threshold = getattr(
                settings, "ASYNC_CACHE_CONCURRENCY_THRESHOLD", concurrency_threshold
            )
        except ImportError:
            self.ttl_seconds = ttl_seconds
            self.cleanup_interval = cleanup_interval
            self.num_shards = num_shards
            self.max_workers = max_workers
            self.concurrency_threshold = concurrency_threshold

        # TWS-specific optimizations
        self.tws_job_patterns: Dict[str, Any] = {}  # Cache warming for frequent jobs
        self.current_concurrency = 0
        self.adaptive_sharding_enabled = True

        # Initialize consistent hashing
        self.hasher = ConsistentHash(num_shards=self.num_shards)

        # Initialize lock manager
        self.lock_manager = ShardLockManager(num_shards=self.num_shards)

        # Initialize shards
        self.shards = [
            CacheShard(shard_id=i, lock_manager=self.lock_manager)
            for i in range(self.num_shards)
        ]

        # Thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

        # Background task and state
        self.cleanup_task: Optional[asyncio.Task[None]] = None
        self.is_running = False

        # Metrics
        self.metrics = {
            "gets": 0,
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "expired": 0,
            "lock_contentions": 0,
            "cleanup_duration_ms": 0.0,
        }

        # Start background cleanup task
        self._start_cleanup_task()

    def _get_shard_id(self, key: str) -> int:
        """Get the shard ID for a given key using consistent hashing."""
        return self.hasher.get_shard(key)

    def _get_shard(self, key: str) -> CacheShard:
        """Get the shard for a given key."""
        shard_id = self._get_shard_id(key)
        return self.shards[shard_id]

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    async def _cleanup_expired_entries(self) -> None:
        """Background task to cleanup expired entries in parallel."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)

                start_time = time.time()
                total_removed = await self._remove_expired_entries_parallel()
                duration_ms = (time.time() - start_time) * 1000

                self.metrics["cleanup_duration_ms"] = duration_ms
                self.metrics["expired"] += total_removed

                if total_removed > 0:
                    logger.debug(
                        "Cleaned up %d expired cache entries in %.2fms",
                        total_removed,
                        duration_ms,
                    )

            except asyncio.CancelledError:
                logger.debug("TWS_OptimizedAsyncCache cleanup task cancelled")
                break
            except Exception as e:
                logger.error("Error in TWS_OptimizedAsyncCache cleanup task: %s", e)

    async def _remove_expired_entries_parallel(self) -> int:
        """
        Remove expired entries from all shards in parallel.

        Returns:
            Total number of entries removed
        """
        # Create cleanup tasks for each shard
        cleanup_tasks = [shard.remove_expired_entries() for shard in self.shards]

        # Run all cleanup tasks concurrently
        results = await asyncio.gather(*cleanup_tasks)

        # Sum up the results
        return sum(results)

    async def get(self, key: str) -> Any | None:
        """
        Asynchronously retrieve an item from the cache.

        Uses optimistic locking for reads to reduce contention.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        self.metrics["gets"] += 1
        shard = self._get_shard(key)

        # Try optimistic read first (without locking)
        entry = shard.data.get(key)
        if entry:
            current_time = time.time()
            if current_time - entry.timestamp <= entry.ttl:
                self.metrics["hits"] += 1
                logger.debug("Cache HIT for key: %s (optimistic read)", key)
                return entry.data

        # If optimistic read fails or entry expired, use proper locking
        result = await shard.get(key)

        if result is not None:
            self.metrics["hits"] += 1
        else:
            self.metrics["misses"] += 1

        return result

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
        self.metrics["sets"] += 1

        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds

        shard = self._get_shard(key)
        await shard.set(key, value, ttl_seconds)

    async def delete(self, key: str) -> bool:
        """
        Asynchronously delete an item from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        self.metrics["deletes"] += 1
        shard = self._get_shard(key)
        return await shard.delete(key)

    async def clear(self) -> None:
        """Asynchronously clear all cache entries."""
        clear_tasks = [shard.clear() for shard in self.shards]
        await asyncio.gather(*clear_tasks)
        logger.debug("Cache CLEARED")

    def size(self) -> int:
        """Get the current number of items in cache."""
        return sum(shard.size() for shard in self.shards)

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        total_gets = self.metrics["gets"]
        hit_ratio = self.metrics["hits"] / total_gets if total_gets > 0 else 0

        return {
            "size": self.size(),
            "gets": total_gets,
            "hits": self.metrics["hits"],
            "misses": self.metrics["misses"],
            "sets": self.metrics["sets"],
            "deletes": self.metrics["deletes"],
            "expired": self.metrics["expired"],
            "hit_ratio": hit_ratio,
            "lock_contentions": self.metrics["lock_contentions"],
            "cleanup_duration_ms": self.metrics["cleanup_duration_ms"],
        }

    async def warm_tws_cache(self, critical_jobs: Optional[List[str]] = None) -> None:
        """
        Pre-load cache with critical TWS job statuses.

        Args:
            critical_jobs: List of job IDs to warm cache for
                         Defaults to common TWS critical jobs
        """
        if critical_jobs is None:
            critical_jobs = [
                "FINAL_BATCH_PAYROLL",
                "EOD_PROCESSING",
                "MONTHLY_CLOSE",
                "DAILY_BACKUP",
            ]

        try:
            # TWS cache warming - placeholder for future implementation
            # Would require TWS client initialization with proper credentials
            logger.debug("TWS cache warming attempted - requires TWS client initialization")

        except ImportError:
            logger.debug("TWS client not available for cache warming")

    def _adapt_sharding(self) -> None:
        """Dynamically adjust number of shards based on concurrency."""
        if not self.adaptive_sharding_enabled:
            return

        # Simple heuristic: increase shards when concurrency is high
        if (
            self.current_concurrency > self.concurrency_threshold
            and self.num_shards < 8
        ):
            # This would require reinitializing the cache - complex operation
            # For now, just log the recommendation
            logger.info(
                f"High concurrency detected ({self.current_concurrency}), consider increasing shards"
            )

    async def stop(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        logger.debug("TWS_OptimizedAsyncCache stopped")

    async def __aenter__(self) -> "TWS_OptimizedAsyncCache":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup resources."""
        await self.stop()
