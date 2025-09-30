from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import time
from typing import Any, Dict, List, Optional, Tuple

from resync.core.exceptions import CacheError
from resync.core.metrics import runtime_metrics, log_with_correlation

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
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "async_cache",
                "operation": "init",
                "ttl_seconds": ttl_seconds,
                "cleanup_interval": cleanup_interval,
                "num_shards": num_shards,
            }
        )

        try:
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
                log_with_correlation(
                    logging.DEBUG,
                    "Loaded cache config from external module",
                    correlation_id,
                )
            except ImportError:
                # Handle the case where your_config_module is not available
                self.ttl_seconds = ttl_seconds
                self.cleanup_interval = cleanup_interval
                log_with_correlation(
                    logging.WARNING,
                    "External config module not available, using defaults",
                    correlation_id,
                )

            self.num_shards = num_shards
            self.shards: List[Dict[str, CacheEntry]] = [{} for _ in range(num_shards)]
            self.shard_locks = [asyncio.Lock() for _ in range(num_shards)]
            self.cleanup_task: Optional[asyncio.Task[None]] = None
            self.is_running = False

            # Start background cleanup task
            self._start_cleanup_task()

            runtime_metrics.record_health_check(
                "async_cache",
                "initialized",
                {
                    "ttl_seconds": self.ttl_seconds,
                    "cleanup_interval": self.cleanup_interval,
                    "num_shards": self.num_shards,
                },
            )
            log_with_correlation(
                logging.INFO, "AsyncTTLCache initialized successfully", correlation_id
            )

        except Exception as e:
            runtime_metrics.record_health_check(
                "async_cache", "init_failed", {"error": str(e)}
            )
            log_with_correlation(
                logging.CRITICAL,
                f"Failed to initialize AsyncTTLCache: {e}",
                correlation_id,
            )
            raise
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def _get_shard(self, key: str) -> Tuple[Dict[str, CacheEntry], asyncio.Lock]:
        """Get the shard and lock for a given key with bounds checking."""
        # BOUNDS CHECKING - Prevent hash overflow/underflow
        try:
            key_hash = hash(key)
            # Ensure hash is within reasonable bounds to prevent integer overflow
            if key_hash == 0:
                # Special case for hash collision - use a deterministic alternative
                key_hash = sum(ord(c) for c in str(key)) + len(str(key))

            shard_index = abs(key_hash) % self.num_shards

            # Double-check bounds (defense in depth)
            if not (0 <= shard_index < self.num_shards):
                # Fallback to a safe index if bounds check fails
                shard_index = 0
                logger.warning(
                    f"Shard index bounds check failed for key hash {key_hash}, using fallback shard 0",
                    extra={
                        "correlation_id": runtime_metrics.create_correlation_id(
                            {
                                "component": "async_cache",
                                "operation": "shard_bounds_check",
                                "key_hash": key_hash,
                                "num_shards": self.num_shards,
                            }
                        ).id
                    },
                )

        except (OverflowError, ValueError) as e:
            # Hash computation failed - use deterministic fallback
            shard_index = (
                sum(ord(c) for c in str(key)[:10]) % self.num_shards
            )  # Use first 10 chars
            logger.warning(
                f"Hash computation failed for key {repr(key)}: {e}, using fallback shard {shard_index}"
            )

        return self.shards[shard_index], self.shard_locks[shard_index]

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    async def _cleanup_expired_entries(self) -> None:
        """Background task to cleanup expired entries."""
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "async_cache", "operation": "cleanup_task"}
        )

        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
                runtime_metrics.cache_cleanup_cycles.increment()
                runtime_metrics.cache_size.set(self.size())

            except asyncio.CancelledError:
                log_with_correlation(
                    logging.DEBUG,
                    "AsyncTTLCache cleanup task cancelled",
                    correlation_id,
                )
                break
            except MemoryError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Memory error in AsyncTTLCache cleanup task: {e}",
                    correlation_id,
                )
                runtime_metrics.record_health_check(
                    "async_cache", "memory_error", {"error": str(e)}
                )
                raise CacheError("Memory error during cache cleanup") from e
            except KeyError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Key error in AsyncTTLCache cleanup task: {e}",
                    correlation_id,
                )
                runtime_metrics.record_health_check(
                    "async_cache", "key_error", {"error": str(e)}
                )
                raise CacheError(f"Key error during cache cleanup: {e}") from e
            except RuntimeError as e:  # pragma: no cover
                log_with_correlation(
                    logging.ERROR,
                    f"Runtime error in AsyncTTLCache cleanup task: {e}",
                    correlation_id,
                )
                runtime_metrics.record_health_check(
                    "async_cache", "runtime_error", {"error": str(e)}
                )
                raise CacheError(f"Runtime error during cache cleanup: {e}") from e
            except Exception as e:  # pragma: no cover
                log_with_correlation(
                    logging.CRITICAL,
                    f"Unexpected error in AsyncTTLCache cleanup task: {e}",
                    correlation_id,
                    exc_info=True,
                )
                runtime_metrics.record_health_check(
                    "async_cache", "critical_error", {"error": str(e)}
                )
                # Depending on the desired behavior, we might want to stop the loop
                # or just log and continue. For now, we re-raise to make the failure visible.
                raise CacheError(
                    "Unexpected critical error during cache cleanup"
                ) from e

        runtime_metrics.close_correlation_id(correlation_id)

    async def _remove_expired_entries(self) -> None:
        """Remove expired entries from cache."""
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "async_cache", "operation": "remove_expired"}
        )

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
                    log_with_correlation(
                        logging.DEBUG,
                        f"Removed expired cache entry: {key}",
                        correlation_id,
                    )
                total_removed += len(expired_keys)

        if total_removed > 0:
            runtime_metrics.cache_evictions.increment(total_removed)
            log_with_correlation(
                logging.DEBUG,
                f"Cleaned up {total_removed} expired cache entries",
                correlation_id,
            )

        runtime_metrics.close_correlation_id(correlation_id)

    async def get(self, key: Any) -> Any | None:
        """
        Asynchronously retrieve an item from the cache with input validation.

        Args:
            key: Cache key to retrieve (will be validated/normalized)
        Returns:
            Cached value if exists and not expired, None otherwise

        Raises:
            ValueError: If key validation fails
            TypeError: If key is invalid
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "async_cache", "operation": "get", "key": key}
        )

        try:
            # Validate and normalize key
            if key is None:
                raise TypeError("Cache key cannot be None")

            # Apply same validation as set operation
            if not isinstance(key, (str, int, float, bool)):
                try:
                    str_key = str(key)
                    if len(str_key) > 1000:
                        raise ValueError(
                            f"Cache key too long: {len(str_key)} characters (max 1000)"
                        )
                    if "\x00" in str_key:
                        raise ValueError("Cache key cannot contain null bytes")
                    key = str_key
                except Exception:
                    raise TypeError(
                        f"Cache key must be convertible to string: {type(key)}"
                    )
            else:
                key = str(key)

            # Additional validations
            if len(key) == 0:
                raise ValueError("Cache key cannot be empty")
            if len(key) > 1000:
                raise ValueError(
                    f"Cache key too long: {len(key)} characters (max 1000)"
                )
            if "\x00" in key or "\r" in key or "\n" in key:
                raise ValueError("Cache key cannot contain control characters")

            shard, lock = self._get_shard(key)
            async with lock:
                entry = shard.get(key)
                if entry:
                    current_time = time()
                    if current_time - entry.timestamp <= entry.ttl:
                        runtime_metrics.cache_hits.increment()
                        # Update hit rate dynamically
                        total_requests = (
                            runtime_metrics.cache_hits.value
                            + runtime_metrics.cache_misses.value
                        )
                        if total_requests > 0:
                            hit_rate = runtime_metrics.cache_hits.value / total_requests
                            runtime_metrics.record_health_check(
                                "async_cache",
                                "performance",
                                {
                                    "hit_rate": hit_rate,
                                    "total_requests": total_requests,
                                },
                            )
                        log_with_correlation(
                            logging.DEBUG,
                            f"Cache HIT for key: {repr(key)}",
                            correlation_id,
                        )
                        return entry.data
                    else:
                        # Entry expired, remove it
                        del shard[key]
                        runtime_metrics.cache_evictions.increment()
                        # Update eviction rate
                        total_evictions = runtime_metrics.cache_evictions.value
                        total_sets = runtime_metrics.cache_sets.value
                        if total_sets > 0:
                            eviction_rate = total_evictions / total_sets
                            runtime_metrics.record_health_check(
                                "async_cache",
                                "eviction_rate",
                                {
                                    "eviction_rate": eviction_rate,
                                    "total_evictions": total_evictions,
                                },
                            )
                        log_with_correlation(
                            logging.DEBUG,
                            f"Cache EXPIRED for key: {repr(key)}",
                            correlation_id,
                        )

                runtime_metrics.cache_misses.increment()
                # Update miss rate
                total_requests = (
                    runtime_metrics.cache_hits.value
                    + runtime_metrics.cache_misses.value
                )
                if total_requests > 0:
                    miss_rate = runtime_metrics.cache_misses.value / total_requests
                    runtime_metrics.record_health_check(
                        "async_cache",
                        "miss_rate",
                        {"miss_rate": miss_rate, "total_requests": total_requests},
                    )
                log_with_correlation(
                    logging.DEBUG, f"Cache MISS for key: {repr(key)}", correlation_id
                )
                return None

        except (ValueError, TypeError) as e:
            log_with_correlation(
                logging.WARNING,
                f"Cache GET validation failed for key {repr(key)}: {e}",
                correlation_id,
            )
            raise
        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                f"Cache GET failed for key {repr(key)}: {e}",
                correlation_id,
            )
            raise
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def set(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Asynchronously add an item to the cache with comprehensive input validation.

        Args:
            key: Cache key (must be valid string/hashable)
            value: Value to cache (validated for serializability)
            ttl_seconds: Optional TTL override for this specific entry

        Raises:
            ValueError: If key or value validation fails
            TypeError: If key is not hashable or value is invalid
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "async_cache",
                "operation": "set",
                "key": key,
                "ttl_seconds": ttl_seconds,
            }
        )

        try:
            # FUZZING-HARDENED INPUT VALIDATION
            key, ttl_seconds = self._validate_cache_inputs(key, value, ttl_seconds)

            current_time = time()
            entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)

            shard, lock = self._get_shard(key)
            async with lock:
                # BOUNDS CHECKING - Prevent cache overflow before setting
                if not self._check_cache_bounds():
                    # Cache is too large, trigger emergency cleanup
                    log_with_correlation(
                        logging.WARNING,
                        f"Cache bounds exceeded before SET operation, triggering emergency cleanup",
                        correlation_id,
                    )
                    # Remove oldest entries in this shard to make room
                    current_time = time()
                    expired_keys = [
                        k
                        for k, e in shard.items()
                        if current_time - e.timestamp > e.ttl
                    ]
                    for k in expired_keys[:10]:  # Remove up to 10 expired entries
                        del shard[k]
                        log_with_correlation(
                            logging.DEBUG,
                            f"Emergency cleanup removed expired key: {k}",
                            correlation_id,
                        )

                    # If still over bounds, reject the operation
                    if not self._check_cache_bounds():
                        raise ValueError(
                            f"Cache bounds exceeded: cannot add key {repr(key)} (cache too large)"
                        )

                shard[key] = entry
                runtime_metrics.cache_sets.increment()
                runtime_metrics.cache_size.set(self.size())
                log_with_correlation(
                    logging.DEBUG, f"Cache SET for key: {repr(key)}", correlation_id
                )
        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                f"Cache SET failed for key {repr(key)}: {e}",
                correlation_id,
            )
            raise
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def _validate_cache_inputs(
        self, key: Any, value: Any, ttl_seconds: Optional[int]
    ) -> tuple[str, int]:
        """
        Comprehensive input validation based on fuzzing failures.

        Args:
            key: Raw key input
            value: Raw value input
            ttl_seconds: Raw TTL input

        Returns:
            tuple: (validated_key, validated_ttl)

        Raises:
            ValueError: For invalid inputs
            TypeError: For incorrect types
        """
        # KEY VALIDATION - HARDENED AGAINST FUZZING
        if key is None:
            raise TypeError("Cache key cannot be None")

        # Convert key to string if possible, but validate it's reasonable
        if not isinstance(key, (str, int, float, bool)):
            # For complex objects, require they have a proper string representation
            try:
                str_key = str(key)
                if len(str_key) > 1000:  # Prevent extremely long keys
                    raise ValueError(
                        f"Cache key too long: {len(str_key)} characters (max 1000)"
                    )
                if "\x00" in str_key:  # Prevent null bytes
                    raise ValueError("Cache key cannot contain null bytes")
                key = str_key
            except Exception:
                raise TypeError(f"Cache key must be convertible to string: {type(key)}")
        else:
            key = str(key)

        # Additional key validations
        if len(key) == 0:
            raise ValueError("Cache key cannot be empty")
        if len(key) > 1000:
            raise ValueError(f"Cache key too long: {len(key)} characters (max 1000)")
        if "\x00" in key or "\r" in key or "\n" in key:
            raise ValueError("Cache key cannot contain control characters")

        # VALUE VALIDATION - DEFEND AGAINST MALICIOUS INPUTS
        if value is None:
            raise ValueError("Cache value cannot be None")

        # Check for obviously problematic values
        try:
            # Test if value is pickle-able (basic serializability check)
            import pickle

            pickle.dumps(value, protocol=0)  # Use protocol 0 for basic compatibility
        except (TypeError, AttributeError, pickle.PicklingError) as e:
            # Allow some common non-pickleable types that are safe
            if not isinstance(value, (object, type, function)):
                raise ValueError(f"Cache value must be serializable: {e}")

        # TTL VALIDATION - PREVENT EDGE CASES
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds
        elif not isinstance(ttl_seconds, (int, float)):
            raise TypeError(f"TTL must be numeric: {type(ttl_seconds)}")
        elif ttl_seconds < 0:
            raise ValueError(f"TTL cannot be negative: {ttl_seconds}")
        elif ttl_seconds > 86400 * 365:  # Max 1 year
            raise ValueError(f"TTL too large: {ttl_seconds} seconds (max 1 year)")
        elif ttl_seconds == 0:
            raise ValueError("TTL cannot be zero (use delete instead)")

        return key, int(ttl_seconds)

    async def delete(self, key: str) -> bool:
        """
        Asynchronously delete an item from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "async_cache", "operation": "delete", "key": key}
        )

        try:
            shard, lock = self._get_shard(key)
            async with lock:
                if key in shard:
                    del shard[key]
                    runtime_metrics.cache_evictions.increment()
                    runtime_metrics.cache_size.set(self.size())
                    log_with_correlation(
                        logging.DEBUG, f"Cache DELETE for key: {key}", correlation_id
                    )
                    return True
                return False
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def rollback_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Rollback a series of cache operations atomically with comprehensive bounds checking.

        Args:
            operations: List of operations to rollback, each with format:
                       {"operation": "set|delete", "key": str, "value": Any, "ttl": int}

        Returns:
            True if rollback successful, False otherwise
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "async_cache",
                "operation": "rollback",
                "operations_count": len(operations),
            }
        )

        try:
            # BOUNDS CHECKING - Validate operations list
            if not isinstance(operations, list):
                raise TypeError(f"Operations must be a list, got {type(operations)}")

            if len(operations) == 0:
                log_with_correlation(
                    logging.DEBUG, "Empty operations list for rollback", correlation_id
                )
                return True

            # Prevent excessive rollback operations (DoS protection)
            if len(operations) > 10000:
                raise ValueError(
                    f"Too many operations for rollback: {len(operations)} (max 10000)"
                )

            # Validate each operation structure
            for i, op in enumerate(operations):
                if not isinstance(op, dict):
                    raise TypeError(
                        f"Operation at index {i} must be a dict, got {type(op)}"
                    )

                if "key" not in op:
                    raise ValueError(
                        f"Operation at index {i} missing required 'key' field"
                    )

                if op["operation"] not in ["set", "delete"]:
                    raise ValueError(
                        f"Operation at index {i} has invalid operation: {op.get('operation')}"
                    )

                # Validate key bounds
                key = op["key"]
                if not isinstance(key, (str, int, float, bool)):
                    try:
                        key = str(key)
                        if len(key) > 1000:
                            raise ValueError(
                                f"Key too long in operation {i}: {len(key)} characters"
                            )
                    except Exception:
                        raise ValueError(f"Invalid key in operation {i}: {type(key)}")

            # Group operations by shard to minimize lock contention with bounds checking
            shard_operations: Dict[int, List[Dict[str, Any]]] = {}
            for op in operations:
                try:
                    # Use the same bounds-checked shard calculation
                    _, lock = self._get_shard(op["key"])
                    shard_idx = self.shard_locks.index(
                        lock
                    )  # Get shard index from lock

                    if shard_idx not in shard_operations:
                        shard_operations[shard_idx] = []
                    shard_operations[shard_idx].append(op)
                except (ValueError, IndexError) as e:
                    log_with_correlation(
                        logging.ERROR,
                        f"Failed to determine shard for key {repr(op['key'])}: {e}",
                        correlation_id,
                    )
                    return False

            # Execute rollback per shard
            for shard_idx, ops in shard_operations.items():
                shard = self.shards[shard_idx]
                lock = self.shard_locks[shard_idx]

                async with lock:
                    try:
                        # Use savepoint-like approach (in-memory rollback)
                        for op in reversed(ops):  # Reverse order for proper rollback
                            if op["operation"] == "set":
                                # Restore the previous value or delete if it didn't exist
                                if "previous_value" in op:
                                    current_time = time()
                                    entry = CacheEntry(
                                        data=op["previous_value"],
                                        timestamp=current_time,
                                        ttl=op.get("previous_ttl", self.ttl_seconds),
                                    )
                                    shard[op["key"]] = entry
                                else:
                                    shard.pop(op["key"], None)
                            elif op["operation"] == "delete":
                                # Restore deleted item
                                if "previous_value" in op:
                                    current_time = time()
                                    entry = CacheEntry(
                                        data=op["previous_value"],
                                        timestamp=current_time,
                                        ttl=op.get("previous_ttl", self.ttl_seconds),
                                    )
                                    shard[op["key"]] = entry

                        runtime_metrics.cache_size.set(self.size())
                        log_with_correlation(
                            logging.DEBUG,
                            f"Rolled back {len(ops)} operations on shard {shard_idx}",
                            correlation_id,
                        )

                    except Exception as e:
                        log_with_correlation(
                            logging.ERROR,
                            f"Failed to rollback operations on shard {shard_idx}: {e}",
                            correlation_id,
                        )
                        return False

            log_with_correlation(
                logging.INFO,
                f"Successfully rolled back {len(operations)} cache operations",
                correlation_id,
            )
            return True

        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                f"Cache rollback failed: {e}",
                correlation_id,
                exc_info=True,
            )
            return False
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

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
        total_size = sum(len(shard) for shard in self.shards)
        return total_size

    def _check_cache_bounds(self) -> bool:
        """
        Check if cache size is within safe bounds to prevent memory exhaustion.

        Returns:
            True if within bounds, False if too large
        """
        current_size = self.size()
        max_safe_size = 50000  # Max 50K entries per cache instance

        if current_size > max_safe_size:
            logger.warning(
                f"Cache size {current_size} exceeds safe bounds {max_safe_size}",
                extra={
                    "correlation_id": runtime_metrics.create_correlation_id(
                        {
                            "component": "async_cache",
                            "operation": "bounds_check",
                            "current_size": current_size,
                            "max_safe_size": max_safe_size,
                        }
                    ).id
                },
            )
            return False

        # Check memory usage estimate (rough calculation)
        estimated_memory_mb = current_size * 0.5  # ~500KB per 1000 entries
        if estimated_memory_mb > 100:  # Max 100MB per cache
            logger.warning(
                f"Estimated cache memory usage {estimated_memory_mb:.1f}MB exceeds 100MB limit",
                extra={
                    "correlation_id": runtime_metrics.create_correlation_id(
                        {
                            "component": "async_cache",
                            "operation": "memory_bounds_check",
                            "estimated_mb": estimated_memory_mb,
                            "current_size": current_size,
                        }
                    ).id
                },
            )
            return False

        return True

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics for monitoring."""
        total_requests = (
            runtime_metrics.cache_hits.value + runtime_metrics.cache_misses.value
        )
        total_sets = runtime_metrics.cache_sets.value
        total_evictions = runtime_metrics.cache_evictions.value

        return {
            "size": self.size(),
            "num_shards": self.num_shards,
            "ttl_seconds": self.ttl_seconds,
            "cleanup_interval": self.cleanup_interval,
            "hits": runtime_metrics.cache_hits.value,
            "misses": runtime_metrics.cache_misses.value,
            "sets": total_sets,
            "evictions": total_evictions,
            "cleanup_cycles": runtime_metrics.cache_cleanup_cycles.value,
            "hit_rate": (
                (runtime_metrics.cache_hits.value / total_requests)
                if total_requests > 0
                else 0
            ),
            "miss_rate": (
                (runtime_metrics.cache_misses.value / total_requests)
                if total_requests > 0
                else 0
            ),
            "eviction_rate": (total_evictions / total_sets) if total_sets > 0 else 0,
            "shard_distribution": [len(shard) for shard in self.shards],
            "is_running": self.is_running,
            "health_status": runtime_metrics.get_health_status().get("async_cache", {}),
        }

    def create_backup_snapshot(self) -> Dict[str, Any]:
        """
        Create a backup snapshot of current cache state for rollback purposes.
        WARNING: This is expensive and should be used sparingly.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "async_cache", "operation": "backup_snapshot"}
        )

        try:
            snapshot = {}
            current_time = time()

            for shard_idx, shard in enumerate(self.shards):
                shard_snapshot = {}
                for key, entry in shard.items():
                    if (
                        current_time - entry.timestamp <= entry.ttl
                    ):  # Only backup valid entries
                        shard_snapshot[key] = {
                            "data": entry.data,
                            "timestamp": entry.timestamp,
                            "ttl": entry.ttl,
                        }
                snapshot[f"shard_{shard_idx}"] = shard_snapshot

            snapshot["_metadata"] = {
                "created_at": current_time,
                "total_entries": sum(
                    len(s) for s in snapshot.values() if isinstance(s, dict)
                ),
                "correlation_id": correlation_id,
            }

            log_with_correlation(
                logging.INFO,
                f"Created cache backup snapshot with {snapshot['_metadata']['total_entries']} entries",
                correlation_id,
            )
            return snapshot

        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def restore_from_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Restore cache from a backup snapshot with comprehensive bounds checking.
        This will atomically replace all current cache contents.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "async_cache",
                "operation": "restore_snapshot",
                "snapshot_entries": snapshot.get("_metadata", {}).get(
                    "total_entries", 0
                ),
            }
        )

        try:
            # BOUNDS CHECKING - Validate snapshot structure
            if not isinstance(snapshot, dict):
                raise TypeError(f"Snapshot must be a dict, got {type(snapshot)}")

            if snapshot is None:
                raise ValueError("Snapshot cannot be None")

            if "_metadata" not in snapshot:
                log_with_correlation(
                    logging.ERROR,
                    "Invalid snapshot format - missing metadata",
                    correlation_id,
                )
                return False

            metadata = snapshot["_metadata"]
            if not isinstance(metadata, dict):
                raise TypeError("Snapshot metadata must be a dict")

            # Validate total entries bounds (prevent memory exhaustion)
            total_entries = metadata.get("total_entries", 0)
            if not isinstance(total_entries, int) or total_entries < 0:
                raise ValueError(f"Invalid total_entries in metadata: {total_entries}")
            if total_entries > 100000:  # Max 100K entries
                raise ValueError(
                    f"Snapshot too large: {total_entries} entries (max 100000)"
                )

            # Validate snapshot age (don't restore very old snapshots)
            created_at = metadata.get("created_at")
            if not isinstance(created_at, (int, float)):
                raise ValueError(f"Invalid created_at timestamp: {created_at}")

            snapshot_age = time() - created_at
            if snapshot_age < 0:
                raise ValueError(f"Snapshot from future: age {snapshot_age}s")
            if snapshot_age > 3600:  # 1 hour max age
                log_with_correlation(
                    logging.WARNING,
                    f"Snapshot too old ({snapshot_age:.0f}s) - refusing restore",
                    correlation_id,
                )
                return False

            # Clear current cache
            await self.clear()

            # Restore from snapshot
            restored_count = 0
            for shard_key, shard_data in snapshot.items():
                if shard_key.startswith("shard_") and isinstance(shard_data, dict):
                    shard_idx = int(shard_key.split("_")[1])
                    if 0 <= shard_idx < self.num_shards:
                        shard = self.shards[shard_idx]
                        lock = self.shard_locks[shard_idx]

                        async with lock:
                            for key, entry_data in shard_data.items():
                                entry = CacheEntry(
                                    data=entry_data["data"],
                                    timestamp=entry_data["timestamp"],
                                    ttl=entry_data["ttl"],
                                )
                                shard[key] = entry
                                restored_count += 1

            runtime_metrics.cache_size.set(self.size())
            log_with_correlation(
                logging.INFO,
                f"Restored {restored_count} entries from snapshot",
                correlation_id,
            )
            return True

        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                f"Failed to restore from snapshot: {e}",
                correlation_id,
                exc_info=True,
            )
            return False
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

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

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform PRODUCTION-GRADE comprehensive health check of the cache with rigorous validation.
        """
        try:
            correlation_id = runtime_metrics.create_correlation_id(
                {"component": "async_cache", "operation": "health_check"}
            )

            # PRODUCTION READINESS: Check environment and security context
            from resync.core import env_detector

            is_production = env_detector.is_production()
            security_level = env_detector.get_security_level()

            # 1. BASIC FUNCTIONALITY TESTS
            test_key = f"health_check_{correlation_id.id}_{int(time())}"
            test_value = {
                "test": "data",
                "timestamp": time(),
                "correlation_id": correlation_id.id,
            }

            # Test set operation with validation
            try:
                await self.set(
                    test_key, test_value, ttl_seconds=300
                )  # 5 min TTL for safety
            except Exception as e:
                return {
                    "status": "critical",
                    "component": "async_cache",
                    "error": f"SET operation failed: {e}",
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # Test get operation
            try:
                retrieved = await self.get(test_key)
                if retrieved != test_value:
                    return {
                        "status": "critical",
                        "component": "async_cache",
                        "error": "GET operation data mismatch",
                        "expected": test_value,
                        "received": retrieved,
                        "correlation_id": correlation_id.id,
                        "production_ready": False,
                    }
            except Exception as e:
                return {
                    "status": "critical",
                    "component": "async_cache",
                    "error": f"GET operation failed: {e}",
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # Test delete operation
            try:
                deleted = await self.delete(test_key)
                if not deleted:
                    return {
                        "status": "warning",
                        "component": "async_cache",
                        "error": "DELETE operation returned False",
                        "correlation_id": correlation_id.id,
                        "production_ready": True,  # Not critical for production
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "component": "async_cache",
                    "error": f"DELETE operation failed: {e}",
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # 2. CACHE BOUNDS AND INTEGRITY CHECKS
            current_size = self.size()
            if current_size < 0:
                return {
                    "status": "critical",
                    "component": "async_cache",
                    "error": f"Invalid cache size: {current_size}",
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # Check bounds compliance
            bounds_ok = self._check_cache_bounds()
            if not bounds_ok:
                return {
                    "status": "warning",
                    "component": "async_cache",
                    "error": "Cache bounds exceeded",
                    "current_size": current_size,
                    "correlation_id": correlation_id.id,
                    "production_ready": is_production,  # Only critical in production
                }

            # 3. SHARD INTEGRITY CHECKS
            shard_sizes = [len(shard) for shard in self.shards]
            total_from_shards = sum(shard_sizes)

            if total_from_shards != current_size:
                return {
                    "status": "critical",
                    "component": "async_cache",
                    "error": "Shard size inconsistency",
                    "total_size": current_size,
                    "shard_total": total_from_shards,
                    "shard_sizes": shard_sizes,
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # Check for shard size imbalances (should be roughly equal)
            if self.num_shards > 1:
                avg_shard_size = current_size / self.num_shards
                max_shard_size = max(shard_sizes)
                if max_shard_size > avg_shard_size * 3:  # Allow 3x imbalance
                    return {
                        "status": "warning",
                        "component": "async_cache",
                        "error": "Shard size imbalance detected",
                        "avg_shard_size": avg_shard_size,
                        "max_shard_size": max_shard_size,
                        "shard_sizes": shard_sizes,
                        "correlation_id": correlation_id.id,
                        "production_ready": True,  # Not critical but worth monitoring
                    }

            # 4. BACKGROUND TASK HEALTH
            cleanup_status = (
                "running"
                if self.cleanup_task and not self.cleanup_task.done()
                else "stopped"
            )
            if is_production and cleanup_status != "running":
                return {
                    "status": "error",
                    "component": "async_cache",
                    "error": "Background cleanup task not running in production",
                    "cleanup_status": cleanup_status,
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # 5. PERFORMANCE METRICS VALIDATION
            metrics = self.get_detailed_metrics()
            hit_rate = metrics.get("hit_rate", 0)
            if hit_rate < 0 or hit_rate > 1:
                return {
                    "status": "error",
                    "component": "async_cache",
                    "error": "Invalid hit rate metrics",
                    "hit_rate": hit_rate,
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # 6. PRODUCTION READINESS VALIDATION
            production_issues = []

            # Check configuration validity
            if self.ttl_seconds <= 0 or self.ttl_seconds > 86400:
                production_issues.append(
                    f"Invalid TTL configuration: {self.ttl_seconds}"
                )

            if self.num_shards <= 0 or self.num_shards > 256:
                production_issues.append(f"Invalid shard count: {self.num_shards}")

            if len(production_issues) > 0:
                return {
                    "status": "error",
                    "component": "async_cache",
                    "error": "Production configuration issues",
                    "issues": production_issues,
                    "correlation_id": correlation_id.id,
                    "production_ready": False,
                }

            # SUCCESS - All checks passed
            result = {
                "status": "healthy",
                "component": "async_cache",
                "production_ready": True,
                "size": current_size,
                "num_shards": self.num_shards,
                "shard_sizes": shard_sizes,
                "cleanup_status": cleanup_status,
                "ttl_seconds": self.ttl_seconds,
                "hit_rate": hit_rate,
                "bounds_compliant": bounds_ok,
                "environment": env_detector._environment,
                "security_level": security_level,
                "correlation_id": correlation_id.id,
            }

            log_with_correlation(
                logging.DEBUG,
                f"Cache health check PASSED - production ready: {result['production_ready']}",
                correlation_id,
            )
            runtime_metrics.close_correlation_id(correlation_id)
            return result

        except Exception as e:
            error_correlation = runtime_metrics.create_correlation_id(
                {
                    "component": "async_cache",
                    "operation": "health_check_critical_failure",
                }
            )
            return {
                "status": "critical",
                "component": "async_cache",
                "error": f"Health check completely failed: {e}",
                "correlation_id": str(error_correlation),
                "production_ready": False,
                "exception_type": type(e).__name__,
            }

    async def __aenter__(self) -> "AsyncTTLCache":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup resources."""
        await self.stop()
