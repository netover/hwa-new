from __future__ import annotations

import asyncio
import logging
from collections import OrderedDict
from dataclasses import dataclass
from time import time as time_func
from typing import Any, Dict, Optional, Tuple

from resync.core.async_cache import AsyncTTLCache
from resync.settings import settings

logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
    In-memory L1 cache with LRU eviction and asyncio.Lock protection.
    """

    def xǁL1Cacheǁ__init____mutmut_orig(self, max_size: int = 1000):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = asyncio.Lock()

    def xǁL1Cacheǁ__init____mutmut_1(self, max_size: int = 1001):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = asyncio.Lock()

    def xǁL1Cacheǁ__init____mutmut_2(self, max_size: int = 1000):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
        """
        self.max_size = None
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = asyncio.Lock()

    def xǁL1Cacheǁ__init____mutmut_3(self, max_size: int = 1000):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float]] = None
        self.lock = asyncio.Lock()

    def xǁL1Cacheǁ__init____mutmut_4(self, max_size: int = 1000):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = None

    xǁL1Cacheǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁL1Cacheǁ__init____mutmut_1": xǁL1Cacheǁ__init____mutmut_1,
        "xǁL1Cacheǁ__init____mutmut_2": xǁL1Cacheǁ__init____mutmut_2,
        "xǁL1Cacheǁ__init____mutmut_3": xǁL1Cacheǁ__init____mutmut_3,
        "xǁL1Cacheǁ__init____mutmut_4": xǁL1Cacheǁ__init____mutmut_4,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁL1Cacheǁ__init____mutmut_orig"),
            object.__getattribute__(self, "xǁL1Cacheǁ__init____mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁL1Cacheǁ__init____mutmut_orig)
    xǁL1Cacheǁ__init____mutmut_orig.__name__ = "xǁL1Cacheǁ__init__"

    async def xǁL1Cacheǁget__mutmut_orig(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(key)  # Move to most recently used
                logger.debug(f"L1 cache HIT for key: {key}")
                return value

            logger.debug(f"L1 cache MISS for key: {key}")
            return None

    async def xǁL1Cacheǁget__mutmut_1(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key not in self.cache:
                value, timestamp = self.cache[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(key)  # Move to most recently used
                logger.debug(f"L1 cache HIT for key: {key}")
                return value

            logger.debug(f"L1 cache MISS for key: {key}")
            return None

    async def xǁL1Cacheǁget__mutmut_2(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = None

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(key)  # Move to most recently used
                logger.debug(f"L1 cache HIT for key: {key}")
                return value

            logger.debug(f"L1 cache MISS for key: {key}")
            return None

    async def xǁL1Cacheǁget__mutmut_3(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(None)  # Move to most recently used
                logger.debug(f"L1 cache HIT for key: {key}")
                return value

            logger.debug(f"L1 cache MISS for key: {key}")
            return None

    async def xǁL1Cacheǁget__mutmut_4(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(key)  # Move to most recently used
                logger.debug(None)
                return value

            logger.debug(f"L1 cache MISS for key: {key}")
            return None

    async def xǁL1Cacheǁget__mutmut_5(self, key: str) -> Optional[Any]:
        """
        Get value from L1 cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]

                # Check if entry is still valid (no TTL in L1, just LRU)
                self.cache.move_to_end(key)  # Move to most recently used
                logger.debug(f"L1 cache HIT for key: {key}")
                return value

            logger.debug(None)
            return None

    xǁL1Cacheǁget__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁL1Cacheǁget__mutmut_1": xǁL1Cacheǁget__mutmut_1,
        "xǁL1Cacheǁget__mutmut_2": xǁL1Cacheǁget__mutmut_2,
        "xǁL1Cacheǁget__mutmut_3": xǁL1Cacheǁget__mutmut_3,
        "xǁL1Cacheǁget__mutmut_4": xǁL1Cacheǁget__mutmut_4,
        "xǁL1Cacheǁget__mutmut_5": xǁL1Cacheǁget__mutmut_5,
    }

    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁL1Cacheǁget__mutmut_orig"),
            object.__getattribute__(self, "xǁL1Cacheǁget__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    get.__signature__ = _mutmut_signature(xǁL1Cacheǁget__mutmut_orig)
    xǁL1Cacheǁget__mutmut_orig.__name__ = "xǁL1Cacheǁget"

    async def xǁL1Cacheǁset__mutmut_orig(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_1(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = None

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_2(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            time_func()

            # Add or update entry
            self.cache[key] = None
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_3(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(None)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_4(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) >= self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_5(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = None  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_6(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=None)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_7(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=True)  # Remove LRU
                logger.debug(f"L1 cache EVICTION for key: {evicted_key}")

    async def xǁL1Cacheǁset__mutmut_8(self, key: str, value: Any) -> None:
        """
        Set value in L1 cache with LRU eviction if needed.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            current_time = time_func()

            # Add or update entry
            self.cache[key] = (value, current_time)
            self.cache.move_to_end(key)  # Move to most recently used

            # Check if we need to evict
            if len(self.cache) > self.max_size:
                evicted_key, _ = self.cache.popitem(last=False)  # Remove LRU
                logger.debug(None)

    xǁL1Cacheǁset__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁL1Cacheǁset__mutmut_1": xǁL1Cacheǁset__mutmut_1,
        "xǁL1Cacheǁset__mutmut_2": xǁL1Cacheǁset__mutmut_2,
        "xǁL1Cacheǁset__mutmut_3": xǁL1Cacheǁset__mutmut_3,
        "xǁL1Cacheǁset__mutmut_4": xǁL1Cacheǁset__mutmut_4,
        "xǁL1Cacheǁset__mutmut_5": xǁL1Cacheǁset__mutmut_5,
        "xǁL1Cacheǁset__mutmut_6": xǁL1Cacheǁset__mutmut_6,
        "xǁL1Cacheǁset__mutmut_7": xǁL1Cacheǁset__mutmut_7,
        "xǁL1Cacheǁset__mutmut_8": xǁL1Cacheǁset__mutmut_8,
    }

    def set(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁL1Cacheǁset__mutmut_orig"),
            object.__getattribute__(self, "xǁL1Cacheǁset__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    set.__signature__ = _mutmut_signature(xǁL1Cacheǁset__mutmut_orig)
    xǁL1Cacheǁset__mutmut_orig.__name__ = "xǁL1Cacheǁset"

    async def xǁL1Cacheǁdelete__mutmut_orig(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"L1 cache DELETE for key: {key}")
                return True
            return False

    async def xǁL1Cacheǁdelete__mutmut_1(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self.lock:
            if key not in self.cache:
                del self.cache[key]
                logger.debug(f"L1 cache DELETE for key: {key}")
                return True
            return False

    async def xǁL1Cacheǁdelete__mutmut_2(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(None)
                return True
            return False

    async def xǁL1Cacheǁdelete__mutmut_3(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"L1 cache DELETE for key: {key}")
                return False
            return False

    async def xǁL1Cacheǁdelete__mutmut_4(self, key: str) -> bool:
        """
        Delete key from L1 cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found and deleted, False otherwise
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"L1 cache DELETE for key: {key}")
                return True
            return True

    xǁL1Cacheǁdelete__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁL1Cacheǁdelete__mutmut_1": xǁL1Cacheǁdelete__mutmut_1,
        "xǁL1Cacheǁdelete__mutmut_2": xǁL1Cacheǁdelete__mutmut_2,
        "xǁL1Cacheǁdelete__mutmut_3": xǁL1Cacheǁdelete__mutmut_3,
        "xǁL1Cacheǁdelete__mutmut_4": xǁL1Cacheǁdelete__mutmut_4,
    }

    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁL1Cacheǁdelete__mutmut_orig"),
            object.__getattribute__(self, "xǁL1Cacheǁdelete__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    delete.__signature__ = _mutmut_signature(xǁL1Cacheǁdelete__mutmut_orig)
    xǁL1Cacheǁdelete__mutmut_orig.__name__ = "xǁL1Cacheǁdelete"

    async def xǁL1Cacheǁclear__mutmut_orig(self) -> None:
        """Clear all entries from L1 cache."""
        async with self.lock:
            self.cache.clear()
            logger.debug("L1 cache CLEARED")

    async def xǁL1Cacheǁclear__mutmut_1(self) -> None:
        """Clear all entries from L1 cache."""
        async with self.lock:
            self.cache.clear()
            logger.debug(None)

    async def xǁL1Cacheǁclear__mutmut_2(self) -> None:
        """Clear all entries from L1 cache."""
        async with self.lock:
            self.cache.clear()
            logger.debug("XXL1 cache CLEAREDXX")

    async def xǁL1Cacheǁclear__mutmut_3(self) -> None:
        """Clear all entries from L1 cache."""
        async with self.lock:
            self.cache.clear()
            logger.debug("l1 cache cleared")

    async def xǁL1Cacheǁclear__mutmut_4(self) -> None:
        """Clear all entries from L1 cache."""
        async with self.lock:
            self.cache.clear()
            logger.debug("L1 CACHE CLEARED")

    xǁL1Cacheǁclear__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁL1Cacheǁclear__mutmut_1": xǁL1Cacheǁclear__mutmut_1,
        "xǁL1Cacheǁclear__mutmut_2": xǁL1Cacheǁclear__mutmut_2,
        "xǁL1Cacheǁclear__mutmut_3": xǁL1Cacheǁclear__mutmut_3,
        "xǁL1Cacheǁclear__mutmut_4": xǁL1Cacheǁclear__mutmut_4,
    }

    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁL1Cacheǁclear__mutmut_orig"),
            object.__getattribute__(self, "xǁL1Cacheǁclear__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    clear.__signature__ = _mutmut_signature(xǁL1Cacheǁclear__mutmut_orig)
    xǁL1Cacheǁclear__mutmut_orig.__name__ = "xǁL1Cacheǁclear"

    def size(self) -> int:
        """Get current size of L1 cache."""
        return len(self.cache)


class CacheHierarchy:
    """
    Two-tier cache hierarchy with L1 (in-memory) and L2 (Redis-backed).

    Priority: L1 read → if miss → L2 read → if miss → fetch from source → write to L2 → write to L1
    Write-through: All writes go to L2 first, then L1
    """

    def xǁCacheHierarchyǁ__init____mutmut_orig(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_1(
        self,
        l1_max_size: int = 1001,
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_2(
        self,
        l1_max_size: int = 1000,
        l2_ttl_seconds: int = 301,
        l2_cleanup_interval: int = 30,
    ):
        """
        Initialize cache hierarchy.

        Args:
            l1_max_size: Maximum entries in L1 cache before LRU eviction
            l2_ttl_seconds: TTL for L2 cache entries
            l2_cleanup_interval: Cleanup interval for L2 cache
        """
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_3(
        self,
        l1_max_size: int = 1000,
        l2_ttl_seconds: int = 300,
        l2_cleanup_interval: int = 31,
    ):
        """
        Initialize cache hierarchy.

        Args:
            l1_max_size: Maximum entries in L1 cache before LRU eviction
            l2_ttl_seconds: TTL for L2 cache entries
            l2_cleanup_interval: Cleanup interval for L2 cache
        """
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_4(
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
        self.l1_cache = None
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_5(
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
        self.l1_cache = L1Cache(max_size=None)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_6(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = None
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_7(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=None, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_8(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(ttl_seconds=l2_ttl_seconds, cleanup_interval=None)
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_9(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(cleanup_interval=l2_cleanup_interval)
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_10(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds,
        )
        self.metrics = CacheMetrics()
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_11(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = None
        self.is_running = False

    def xǁCacheHierarchyǁ__init____mutmut_12(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = None

    def xǁCacheHierarchyǁ__init____mutmut_13(
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
        self.l1_cache = L1Cache(max_size=l1_max_size)
        self.l2_cache = AsyncTTLCache(
            ttl_seconds=l2_ttl_seconds, cleanup_interval=l2_cleanup_interval
        )
        self.metrics = CacheMetrics()
        self.is_running = True

    xǁCacheHierarchyǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁ__init____mutmut_1": xǁCacheHierarchyǁ__init____mutmut_1,
        "xǁCacheHierarchyǁ__init____mutmut_2": xǁCacheHierarchyǁ__init____mutmut_2,
        "xǁCacheHierarchyǁ__init____mutmut_3": xǁCacheHierarchyǁ__init____mutmut_3,
        "xǁCacheHierarchyǁ__init____mutmut_4": xǁCacheHierarchyǁ__init____mutmut_4,
        "xǁCacheHierarchyǁ__init____mutmut_5": xǁCacheHierarchyǁ__init____mutmut_5,
        "xǁCacheHierarchyǁ__init____mutmut_6": xǁCacheHierarchyǁ__init____mutmut_6,
        "xǁCacheHierarchyǁ__init____mutmut_7": xǁCacheHierarchyǁ__init____mutmut_7,
        "xǁCacheHierarchyǁ__init____mutmut_8": xǁCacheHierarchyǁ__init____mutmut_8,
        "xǁCacheHierarchyǁ__init____mutmut_9": xǁCacheHierarchyǁ__init____mutmut_9,
        "xǁCacheHierarchyǁ__init____mutmut_10": xǁCacheHierarchyǁ__init____mutmut_10,
        "xǁCacheHierarchyǁ__init____mutmut_11": xǁCacheHierarchyǁ__init____mutmut_11,
        "xǁCacheHierarchyǁ__init____mutmut_12": xǁCacheHierarchyǁ__init____mutmut_12,
        "xǁCacheHierarchyǁ__init____mutmut_13": xǁCacheHierarchyǁ__init____mutmut_13,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁ__init____mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁ__init____mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁCacheHierarchyǁ__init____mutmut_orig)
    xǁCacheHierarchyǁ__init____mutmut_orig.__name__ = "xǁCacheHierarchyǁ__init__"

    async def xǁCacheHierarchyǁstart__mutmut_orig(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info("CacheHierarchy started")

    async def xǁCacheHierarchyǁstart__mutmut_1(self) -> None:
        """Start the cache hierarchy."""
        if self.is_running:
            self.is_running = True
            logger.info("CacheHierarchy started")

    async def xǁCacheHierarchyǁstart__mutmut_2(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = None
            logger.info("CacheHierarchy started")

    async def xǁCacheHierarchyǁstart__mutmut_3(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = False
            logger.info("CacheHierarchy started")

    async def xǁCacheHierarchyǁstart__mutmut_4(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info(None)

    async def xǁCacheHierarchyǁstart__mutmut_5(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info("XXCacheHierarchy startedXX")

    async def xǁCacheHierarchyǁstart__mutmut_6(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info("cachehierarchy started")

    async def xǁCacheHierarchyǁstart__mutmut_7(self) -> None:
        """Start the cache hierarchy."""
        if not self.is_running:
            self.is_running = True
            logger.info("CACHEHIERARCHY STARTED")

    xǁCacheHierarchyǁstart__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁstart__mutmut_1": xǁCacheHierarchyǁstart__mutmut_1,
        "xǁCacheHierarchyǁstart__mutmut_2": xǁCacheHierarchyǁstart__mutmut_2,
        "xǁCacheHierarchyǁstart__mutmut_3": xǁCacheHierarchyǁstart__mutmut_3,
        "xǁCacheHierarchyǁstart__mutmut_4": xǁCacheHierarchyǁstart__mutmut_4,
        "xǁCacheHierarchyǁstart__mutmut_5": xǁCacheHierarchyǁstart__mutmut_5,
        "xǁCacheHierarchyǁstart__mutmut_6": xǁCacheHierarchyǁstart__mutmut_6,
        "xǁCacheHierarchyǁstart__mutmut_7": xǁCacheHierarchyǁstart__mutmut_7,
    }

    def start(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁstart__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁstart__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    start.__signature__ = _mutmut_signature(xǁCacheHierarchyǁstart__mutmut_orig)
    xǁCacheHierarchyǁstart__mutmut_orig.__name__ = "xǁCacheHierarchyǁstart"

    async def xǁCacheHierarchyǁstop__mutmut_orig(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info("CacheHierarchy stopped")

    async def xǁCacheHierarchyǁstop__mutmut_1(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = None
            await self.l2_cache.stop()
            logger.info("CacheHierarchy stopped")

    async def xǁCacheHierarchyǁstop__mutmut_2(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = True
            await self.l2_cache.stop()
            logger.info("CacheHierarchy stopped")

    async def xǁCacheHierarchyǁstop__mutmut_3(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info(None)

    async def xǁCacheHierarchyǁstop__mutmut_4(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info("XXCacheHierarchy stoppedXX")

    async def xǁCacheHierarchyǁstop__mutmut_5(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info("cachehierarchy stopped")

    async def xǁCacheHierarchyǁstop__mutmut_6(self) -> None:
        """Stop the cache hierarchy."""
        if self.is_running:
            self.is_running = False
            await self.l2_cache.stop()
            logger.info("CACHEHIERARCHY STOPPED")

    xǁCacheHierarchyǁstop__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁstop__mutmut_1": xǁCacheHierarchyǁstop__mutmut_1,
        "xǁCacheHierarchyǁstop__mutmut_2": xǁCacheHierarchyǁstop__mutmut_2,
        "xǁCacheHierarchyǁstop__mutmut_3": xǁCacheHierarchyǁstop__mutmut_3,
        "xǁCacheHierarchyǁstop__mutmut_4": xǁCacheHierarchyǁstop__mutmut_4,
        "xǁCacheHierarchyǁstop__mutmut_5": xǁCacheHierarchyǁstop__mutmut_5,
        "xǁCacheHierarchyǁstop__mutmut_6": xǁCacheHierarchyǁstop__mutmut_6,
    }

    def stop(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁstop__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁstop__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    stop.__signature__ = _mutmut_signature(xǁCacheHierarchyǁstop__mutmut_orig)
    xǁCacheHierarchyǁstop__mutmut_orig.__name__ = "xǁCacheHierarchyǁstop"

    async def xǁCacheHierarchyǁget__mutmut_orig(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_1(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = None
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_2(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets = 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_3(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets -= 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_4(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 2

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_5(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = None
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_6(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = None
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_7(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(None)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_8(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = None
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_9(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() + l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_10(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = None  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_11(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) * 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_12(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency - l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_13(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 3  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_14(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_15(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits = 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_16(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits -= 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_17(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 2
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_18(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(None)
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_19(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency / 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_20(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1001:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_21(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses = 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_22(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses -= 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_23(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 2

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_24(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = None
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_25(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = None
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_26(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(None)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_27(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = None
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_28(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() + l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_29(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = None  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_30(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) * 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_31(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency - l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_32(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 3  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_33(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_34(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits = 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_35(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits -= 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_36(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 2
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_37(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(None, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_38(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, None)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_39(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_40(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(
                key,
            )
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_41(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(None)
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_42(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency / 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_43(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1001:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_44(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses = 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_45(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses -= 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_46(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 2
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_47(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = None
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_48(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() + start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_49(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = None  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_50(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) * 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_51(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency - miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_52(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 3  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_53(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(None)
        return None

    async def xǁCacheHierarchyǁget__mutmut_54(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency / 1000:.2f}ms"
        )
        return None

    async def xǁCacheHierarchyǁget__mutmut_55(self, key: str) -> Optional[Any]:
        """
        Get value from cache hierarchy with priority L1 → L2.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        start_time = time_func()
        self.metrics.total_gets += 1

        # Try L1 first (fastest)
        l1_start = time_func()
        l1_value = await self.l1_cache.get(key)
        l1_latency = time_func() - l1_start
        self.metrics.l1_get_latency = (
            self.metrics.l1_get_latency + l1_latency
        ) / 2  # Running average

        if l1_value is not None:
            self.metrics.l1_hits += 1
            logger.debug(
                f"Cache HIERARCHY HIT (L1) for key: {key}, latency: {l1_latency * 1000:.2f}ms"
            )
            return l1_value

        self.metrics.l1_misses += 1

        # Try L2 if L1 miss
        l2_start = time_func()
        l2_value = await self.l2_cache.get(key)
        l2_latency = time_func() - l2_start
        self.metrics.l2_get_latency = (
            self.metrics.l2_get_latency + l2_latency
        ) / 2  # Running average

        if l2_value is not None:
            self.metrics.l2_hits += 1
            # Write through to L1 for hot data
            await self.l1_cache.set(key, l2_value)
            logger.debug(
                f"Cache HIERARCHY HIT (L2) for key: {key}, latency: {l2_latency * 1000:.2f}ms"
            )
            return l2_value

        self.metrics.l2_misses += 1
        miss_latency = time_func() - start_time
        self.metrics.miss_latency = (
            self.metrics.miss_latency + miss_latency
        ) / 2  # Running average

        logger.debug(
            f"Cache HIERARCHY MISS for key: {key}, total latency: {miss_latency * 1001:.2f}ms"
        )
        return None

    xǁCacheHierarchyǁget__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁget__mutmut_1": xǁCacheHierarchyǁget__mutmut_1,
        "xǁCacheHierarchyǁget__mutmut_2": xǁCacheHierarchyǁget__mutmut_2,
        "xǁCacheHierarchyǁget__mutmut_3": xǁCacheHierarchyǁget__mutmut_3,
        "xǁCacheHierarchyǁget__mutmut_4": xǁCacheHierarchyǁget__mutmut_4,
        "xǁCacheHierarchyǁget__mutmut_5": xǁCacheHierarchyǁget__mutmut_5,
        "xǁCacheHierarchyǁget__mutmut_6": xǁCacheHierarchyǁget__mutmut_6,
        "xǁCacheHierarchyǁget__mutmut_7": xǁCacheHierarchyǁget__mutmut_7,
        "xǁCacheHierarchyǁget__mutmut_8": xǁCacheHierarchyǁget__mutmut_8,
        "xǁCacheHierarchyǁget__mutmut_9": xǁCacheHierarchyǁget__mutmut_9,
        "xǁCacheHierarchyǁget__mutmut_10": xǁCacheHierarchyǁget__mutmut_10,
        "xǁCacheHierarchyǁget__mutmut_11": xǁCacheHierarchyǁget__mutmut_11,
        "xǁCacheHierarchyǁget__mutmut_12": xǁCacheHierarchyǁget__mutmut_12,
        "xǁCacheHierarchyǁget__mutmut_13": xǁCacheHierarchyǁget__mutmut_13,
        "xǁCacheHierarchyǁget__mutmut_14": xǁCacheHierarchyǁget__mutmut_14,
        "xǁCacheHierarchyǁget__mutmut_15": xǁCacheHierarchyǁget__mutmut_15,
        "xǁCacheHierarchyǁget__mutmut_16": xǁCacheHierarchyǁget__mutmut_16,
        "xǁCacheHierarchyǁget__mutmut_17": xǁCacheHierarchyǁget__mutmut_17,
        "xǁCacheHierarchyǁget__mutmut_18": xǁCacheHierarchyǁget__mutmut_18,
        "xǁCacheHierarchyǁget__mutmut_19": xǁCacheHierarchyǁget__mutmut_19,
        "xǁCacheHierarchyǁget__mutmut_20": xǁCacheHierarchyǁget__mutmut_20,
        "xǁCacheHierarchyǁget__mutmut_21": xǁCacheHierarchyǁget__mutmut_21,
        "xǁCacheHierarchyǁget__mutmut_22": xǁCacheHierarchyǁget__mutmut_22,
        "xǁCacheHierarchyǁget__mutmut_23": xǁCacheHierarchyǁget__mutmut_23,
        "xǁCacheHierarchyǁget__mutmut_24": xǁCacheHierarchyǁget__mutmut_24,
        "xǁCacheHierarchyǁget__mutmut_25": xǁCacheHierarchyǁget__mutmut_25,
        "xǁCacheHierarchyǁget__mutmut_26": xǁCacheHierarchyǁget__mutmut_26,
        "xǁCacheHierarchyǁget__mutmut_27": xǁCacheHierarchyǁget__mutmut_27,
        "xǁCacheHierarchyǁget__mutmut_28": xǁCacheHierarchyǁget__mutmut_28,
        "xǁCacheHierarchyǁget__mutmut_29": xǁCacheHierarchyǁget__mutmut_29,
        "xǁCacheHierarchyǁget__mutmut_30": xǁCacheHierarchyǁget__mutmut_30,
        "xǁCacheHierarchyǁget__mutmut_31": xǁCacheHierarchyǁget__mutmut_31,
        "xǁCacheHierarchyǁget__mutmut_32": xǁCacheHierarchyǁget__mutmut_32,
        "xǁCacheHierarchyǁget__mutmut_33": xǁCacheHierarchyǁget__mutmut_33,
        "xǁCacheHierarchyǁget__mutmut_34": xǁCacheHierarchyǁget__mutmut_34,
        "xǁCacheHierarchyǁget__mutmut_35": xǁCacheHierarchyǁget__mutmut_35,
        "xǁCacheHierarchyǁget__mutmut_36": xǁCacheHierarchyǁget__mutmut_36,
        "xǁCacheHierarchyǁget__mutmut_37": xǁCacheHierarchyǁget__mutmut_37,
        "xǁCacheHierarchyǁget__mutmut_38": xǁCacheHierarchyǁget__mutmut_38,
        "xǁCacheHierarchyǁget__mutmut_39": xǁCacheHierarchyǁget__mutmut_39,
        "xǁCacheHierarchyǁget__mutmut_40": xǁCacheHierarchyǁget__mutmut_40,
        "xǁCacheHierarchyǁget__mutmut_41": xǁCacheHierarchyǁget__mutmut_41,
        "xǁCacheHierarchyǁget__mutmut_42": xǁCacheHierarchyǁget__mutmut_42,
        "xǁCacheHierarchyǁget__mutmut_43": xǁCacheHierarchyǁget__mutmut_43,
        "xǁCacheHierarchyǁget__mutmut_44": xǁCacheHierarchyǁget__mutmut_44,
        "xǁCacheHierarchyǁget__mutmut_45": xǁCacheHierarchyǁget__mutmut_45,
        "xǁCacheHierarchyǁget__mutmut_46": xǁCacheHierarchyǁget__mutmut_46,
        "xǁCacheHierarchyǁget__mutmut_47": xǁCacheHierarchyǁget__mutmut_47,
        "xǁCacheHierarchyǁget__mutmut_48": xǁCacheHierarchyǁget__mutmut_48,
        "xǁCacheHierarchyǁget__mutmut_49": xǁCacheHierarchyǁget__mutmut_49,
        "xǁCacheHierarchyǁget__mutmut_50": xǁCacheHierarchyǁget__mutmut_50,
        "xǁCacheHierarchyǁget__mutmut_51": xǁCacheHierarchyǁget__mutmut_51,
        "xǁCacheHierarchyǁget__mutmut_52": xǁCacheHierarchyǁget__mutmut_52,
        "xǁCacheHierarchyǁget__mutmut_53": xǁCacheHierarchyǁget__mutmut_53,
        "xǁCacheHierarchyǁget__mutmut_54": xǁCacheHierarchyǁget__mutmut_54,
        "xǁCacheHierarchyǁget__mutmut_55": xǁCacheHierarchyǁget__mutmut_55,
    }

    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁget__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁget__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    get.__signature__ = _mutmut_signature(xǁCacheHierarchyǁget__mutmut_orig)
    xǁCacheHierarchyǁget__mutmut_orig.__name__ = "xǁCacheHierarchyǁget"

    async def xǁCacheHierarchyǁset__mutmut_orig(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_1(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets = 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_2(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets -= 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_3(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 2

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_4(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(None, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_5(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, None, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_6(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, None)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_7(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_8(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_9(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(
            key,
            value,
        )

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_10(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(None, value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_11(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, None)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_12(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(value)

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_13(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(
            key,
        )

        logger.debug(f"Cache HIERARCHY SET for key: {key}")

    async def xǁCacheHierarchyǁset__mutmut_14(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value in cache hierarchy with write-through pattern.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(None)

    xǁCacheHierarchyǁset__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁset__mutmut_1": xǁCacheHierarchyǁset__mutmut_1,
        "xǁCacheHierarchyǁset__mutmut_2": xǁCacheHierarchyǁset__mutmut_2,
        "xǁCacheHierarchyǁset__mutmut_3": xǁCacheHierarchyǁset__mutmut_3,
        "xǁCacheHierarchyǁset__mutmut_4": xǁCacheHierarchyǁset__mutmut_4,
        "xǁCacheHierarchyǁset__mutmut_5": xǁCacheHierarchyǁset__mutmut_5,
        "xǁCacheHierarchyǁset__mutmut_6": xǁCacheHierarchyǁset__mutmut_6,
        "xǁCacheHierarchyǁset__mutmut_7": xǁCacheHierarchyǁset__mutmut_7,
        "xǁCacheHierarchyǁset__mutmut_8": xǁCacheHierarchyǁset__mutmut_8,
        "xǁCacheHierarchyǁset__mutmut_9": xǁCacheHierarchyǁset__mutmut_9,
        "xǁCacheHierarchyǁset__mutmut_10": xǁCacheHierarchyǁset__mutmut_10,
        "xǁCacheHierarchyǁset__mutmut_11": xǁCacheHierarchyǁset__mutmut_11,
        "xǁCacheHierarchyǁset__mutmut_12": xǁCacheHierarchyǁset__mutmut_12,
        "xǁCacheHierarchyǁset__mutmut_13": xǁCacheHierarchyǁset__mutmut_13,
        "xǁCacheHierarchyǁset__mutmut_14": xǁCacheHierarchyǁset__mutmut_14,
    }

    def set(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁset__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁset__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    set.__signature__ = _mutmut_signature(xǁCacheHierarchyǁset__mutmut_orig)
    xǁCacheHierarchyǁset__mutmut_orig.__name__ = "xǁCacheHierarchyǁset"

    async def xǁCacheHierarchyǁset_from_source__mutmut_orig(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_1(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets = 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_2(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets -= 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_3(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 2

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_4(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(None, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_5(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, None, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_6(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, None)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_7(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_8(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_9(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(
            key,
            value,
        )

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_10(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(None, value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_11(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, None)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_12(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(value)

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_13(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(
            key,
        )

        logger.debug(f"Cache HIERARCHY SET_FROM_SOURCE for key: {key}")

    async def xǁCacheHierarchyǁset_from_source__mutmut_14(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Set value after fetching from source (bypasses normal write-through).

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (affects L2 only)
        """
        self.metrics.total_sets += 1

        # Write to L2 first (persistent)
        await self.l2_cache.set(key, value, ttl_seconds)

        # Write to L1 (fast access)
        await self.l1_cache.set(key, value)

        logger.debug(None)

    xǁCacheHierarchyǁset_from_source__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁset_from_source__mutmut_1": xǁCacheHierarchyǁset_from_source__mutmut_1,
        "xǁCacheHierarchyǁset_from_source__mutmut_2": xǁCacheHierarchyǁset_from_source__mutmut_2,
        "xǁCacheHierarchyǁset_from_source__mutmut_3": xǁCacheHierarchyǁset_from_source__mutmut_3,
        "xǁCacheHierarchyǁset_from_source__mutmut_4": xǁCacheHierarchyǁset_from_source__mutmut_4,
        "xǁCacheHierarchyǁset_from_source__mutmut_5": xǁCacheHierarchyǁset_from_source__mutmut_5,
        "xǁCacheHierarchyǁset_from_source__mutmut_6": xǁCacheHierarchyǁset_from_source__mutmut_6,
        "xǁCacheHierarchyǁset_from_source__mutmut_7": xǁCacheHierarchyǁset_from_source__mutmut_7,
        "xǁCacheHierarchyǁset_from_source__mutmut_8": xǁCacheHierarchyǁset_from_source__mutmut_8,
        "xǁCacheHierarchyǁset_from_source__mutmut_9": xǁCacheHierarchyǁset_from_source__mutmut_9,
        "xǁCacheHierarchyǁset_from_source__mutmut_10": xǁCacheHierarchyǁset_from_source__mutmut_10,
        "xǁCacheHierarchyǁset_from_source__mutmut_11": xǁCacheHierarchyǁset_from_source__mutmut_11,
        "xǁCacheHierarchyǁset_from_source__mutmut_12": xǁCacheHierarchyǁset_from_source__mutmut_12,
        "xǁCacheHierarchyǁset_from_source__mutmut_13": xǁCacheHierarchyǁset_from_source__mutmut_13,
        "xǁCacheHierarchyǁset_from_source__mutmut_14": xǁCacheHierarchyǁset_from_source__mutmut_14,
    }

    def set_from_source(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁCacheHierarchyǁset_from_source__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁCacheHierarchyǁset_from_source__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    set_from_source.__signature__ = _mutmut_signature(
        xǁCacheHierarchyǁset_from_source__mutmut_orig
    )
    xǁCacheHierarchyǁset_from_source__mutmut_orig.__name__ = (
        "xǁCacheHierarchyǁset_from_source"
    )

    async def xǁCacheHierarchyǁdelete__mutmut_orig(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_1(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = None
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_2(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(None)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_3(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = None

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_4(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(None)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_5(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted and l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_6(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(None)
            return True
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_7(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return False
        return False

    async def xǁCacheHierarchyǁdelete__mutmut_8(self, key: str) -> bool:
        """
        Delete key from both cache tiers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was found in at least one tier
        """
        l1_deleted = await self.l1_cache.delete(key)
        l2_deleted = await self.l2_cache.delete(key)

        if l1_deleted or l2_deleted:
            logger.debug(f"Cache HIERARCHY DELETE for key: {key}")
            return True
        return True

    xǁCacheHierarchyǁdelete__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁdelete__mutmut_1": xǁCacheHierarchyǁdelete__mutmut_1,
        "xǁCacheHierarchyǁdelete__mutmut_2": xǁCacheHierarchyǁdelete__mutmut_2,
        "xǁCacheHierarchyǁdelete__mutmut_3": xǁCacheHierarchyǁdelete__mutmut_3,
        "xǁCacheHierarchyǁdelete__mutmut_4": xǁCacheHierarchyǁdelete__mutmut_4,
        "xǁCacheHierarchyǁdelete__mutmut_5": xǁCacheHierarchyǁdelete__mutmut_5,
        "xǁCacheHierarchyǁdelete__mutmut_6": xǁCacheHierarchyǁdelete__mutmut_6,
        "xǁCacheHierarchyǁdelete__mutmut_7": xǁCacheHierarchyǁdelete__mutmut_7,
        "xǁCacheHierarchyǁdelete__mutmut_8": xǁCacheHierarchyǁdelete__mutmut_8,
    }

    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁdelete__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁdelete__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    delete.__signature__ = _mutmut_signature(xǁCacheHierarchyǁdelete__mutmut_orig)
    xǁCacheHierarchyǁdelete__mutmut_orig.__name__ = "xǁCacheHierarchyǁdelete"

    async def xǁCacheHierarchyǁclear__mutmut_orig(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug("Cache HIERARCHY CLEARED")

    async def xǁCacheHierarchyǁclear__mutmut_1(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug(None)

    async def xǁCacheHierarchyǁclear__mutmut_2(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug("XXCache HIERARCHY CLEAREDXX")

    async def xǁCacheHierarchyǁclear__mutmut_3(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug("cache hierarchy cleared")

    async def xǁCacheHierarchyǁclear__mutmut_4(self) -> None:
        """Clear all entries from both cache tiers."""
        await self.l1_cache.clear()
        await self.l2_cache.clear()
        logger.debug("CACHE HIERARCHY CLEARED")

    xǁCacheHierarchyǁclear__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁclear__mutmut_1": xǁCacheHierarchyǁclear__mutmut_1,
        "xǁCacheHierarchyǁclear__mutmut_2": xǁCacheHierarchyǁclear__mutmut_2,
        "xǁCacheHierarchyǁclear__mutmut_3": xǁCacheHierarchyǁclear__mutmut_3,
        "xǁCacheHierarchyǁclear__mutmut_4": xǁCacheHierarchyǁclear__mutmut_4,
    }

    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁclear__mutmut_orig"),
            object.__getattribute__(self, "xǁCacheHierarchyǁclear__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    clear.__signature__ = _mutmut_signature(xǁCacheHierarchyǁclear__mutmut_orig)
    xǁCacheHierarchyǁclear__mutmut_orig.__name__ = "xǁCacheHierarchyǁclear"

    def size(self) -> Tuple[int, int]:
        """Get sizes of both cache tiers."""
        return self.l1_cache.size(), self.l2_cache.size()

    def xǁCacheHierarchyǁget_metrics__mutmut_orig(self) -> Dict[str, Any]:
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

    def xǁCacheHierarchyǁget_metrics__mutmut_1(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = None
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

    def xǁCacheHierarchyǁget_metrics__mutmut_2(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "XXl1_sizeXX": l1_size,
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

    def xǁCacheHierarchyǁget_metrics__mutmut_3(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "L1_SIZE": l1_size,
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

    def xǁCacheHierarchyǁget_metrics__mutmut_4(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "XXl2_sizeXX": l2_size,
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

    def xǁCacheHierarchyǁget_metrics__mutmut_5(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "L2_SIZE": l2_size,
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

    def xǁCacheHierarchyǁget_metrics__mutmut_6(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "XXl1_hit_ratioXX": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_7(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "L1_HIT_RATIO": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_8(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "XXl2_hit_ratioXX": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_9(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "L2_HIT_RATIO": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_10(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "XXoverall_hit_ratioXX": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_11(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "OVERALL_HIT_RATIO": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_12(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "XXtotal_getsXX": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_13(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "TOTAL_GETS": self.metrics.total_gets,
            "total_sets": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_14(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "XXtotal_setsXX": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_15(self) -> Dict[str, Any]:
        """Get comprehensive cache metrics."""
        l1_size, l2_size = self.size()
        return {
            "l1_size": l1_size,
            "l2_size": l2_size,
            "l1_hit_ratio": self.metrics.l1_hit_ratio,
            "l2_hit_ratio": self.metrics.l2_hit_ratio,
            "overall_hit_ratio": self.metrics.overall_hit_ratio,
            "total_gets": self.metrics.total_gets,
            "TOTAL_SETS": self.metrics.total_sets,
            "l1_evictions": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_16(self) -> Dict[str, Any]:
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
            "XXl1_evictionsXX": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_17(self) -> Dict[str, Any]:
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
            "L1_EVICTIONS": self.metrics.l1_evictions,
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_18(self) -> Dict[str, Any]:
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
            "XXavg_l1_get_latency_msXX": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_19(self) -> Dict[str, Any]:
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
            "AVG_L1_GET_LATENCY_MS": self.metrics.l1_get_latency * 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_20(self) -> Dict[str, Any]:
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
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency / 1000,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_21(self) -> Dict[str, Any]:
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
            "avg_l1_get_latency_ms": self.metrics.l1_get_latency * 1001,
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_22(self) -> Dict[str, Any]:
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
            "XXavg_l2_get_latency_msXX": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_23(self) -> Dict[str, Any]:
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
            "AVG_L2_GET_LATENCY_MS": self.metrics.l2_get_latency * 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_24(self) -> Dict[str, Any]:
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
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency / 1000,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_25(self) -> Dict[str, Any]:
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
            "avg_l2_get_latency_ms": self.metrics.l2_get_latency * 1001,
            "avg_miss_latency_ms": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_26(self) -> Dict[str, Any]:
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
            "XXavg_miss_latency_msXX": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_27(self) -> Dict[str, Any]:
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
            "AVG_MISS_LATENCY_MS": self.metrics.miss_latency * 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_28(self) -> Dict[str, Any]:
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
            "avg_miss_latency_ms": self.metrics.miss_latency / 1000,
        }

    def xǁCacheHierarchyǁget_metrics__mutmut_29(self) -> Dict[str, Any]:
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
            "avg_miss_latency_ms": self.metrics.miss_latency * 1001,
        }

    xǁCacheHierarchyǁget_metrics__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁCacheHierarchyǁget_metrics__mutmut_1": xǁCacheHierarchyǁget_metrics__mutmut_1,
        "xǁCacheHierarchyǁget_metrics__mutmut_2": xǁCacheHierarchyǁget_metrics__mutmut_2,
        "xǁCacheHierarchyǁget_metrics__mutmut_3": xǁCacheHierarchyǁget_metrics__mutmut_3,
        "xǁCacheHierarchyǁget_metrics__mutmut_4": xǁCacheHierarchyǁget_metrics__mutmut_4,
        "xǁCacheHierarchyǁget_metrics__mutmut_5": xǁCacheHierarchyǁget_metrics__mutmut_5,
        "xǁCacheHierarchyǁget_metrics__mutmut_6": xǁCacheHierarchyǁget_metrics__mutmut_6,
        "xǁCacheHierarchyǁget_metrics__mutmut_7": xǁCacheHierarchyǁget_metrics__mutmut_7,
        "xǁCacheHierarchyǁget_metrics__mutmut_8": xǁCacheHierarchyǁget_metrics__mutmut_8,
        "xǁCacheHierarchyǁget_metrics__mutmut_9": xǁCacheHierarchyǁget_metrics__mutmut_9,
        "xǁCacheHierarchyǁget_metrics__mutmut_10": xǁCacheHierarchyǁget_metrics__mutmut_10,
        "xǁCacheHierarchyǁget_metrics__mutmut_11": xǁCacheHierarchyǁget_metrics__mutmut_11,
        "xǁCacheHierarchyǁget_metrics__mutmut_12": xǁCacheHierarchyǁget_metrics__mutmut_12,
        "xǁCacheHierarchyǁget_metrics__mutmut_13": xǁCacheHierarchyǁget_metrics__mutmut_13,
        "xǁCacheHierarchyǁget_metrics__mutmut_14": xǁCacheHierarchyǁget_metrics__mutmut_14,
        "xǁCacheHierarchyǁget_metrics__mutmut_15": xǁCacheHierarchyǁget_metrics__mutmut_15,
        "xǁCacheHierarchyǁget_metrics__mutmut_16": xǁCacheHierarchyǁget_metrics__mutmut_16,
        "xǁCacheHierarchyǁget_metrics__mutmut_17": xǁCacheHierarchyǁget_metrics__mutmut_17,
        "xǁCacheHierarchyǁget_metrics__mutmut_18": xǁCacheHierarchyǁget_metrics__mutmut_18,
        "xǁCacheHierarchyǁget_metrics__mutmut_19": xǁCacheHierarchyǁget_metrics__mutmut_19,
        "xǁCacheHierarchyǁget_metrics__mutmut_20": xǁCacheHierarchyǁget_metrics__mutmut_20,
        "xǁCacheHierarchyǁget_metrics__mutmut_21": xǁCacheHierarchyǁget_metrics__mutmut_21,
        "xǁCacheHierarchyǁget_metrics__mutmut_22": xǁCacheHierarchyǁget_metrics__mutmut_22,
        "xǁCacheHierarchyǁget_metrics__mutmut_23": xǁCacheHierarchyǁget_metrics__mutmut_23,
        "xǁCacheHierarchyǁget_metrics__mutmut_24": xǁCacheHierarchyǁget_metrics__mutmut_24,
        "xǁCacheHierarchyǁget_metrics__mutmut_25": xǁCacheHierarchyǁget_metrics__mutmut_25,
        "xǁCacheHierarchyǁget_metrics__mutmut_26": xǁCacheHierarchyǁget_metrics__mutmut_26,
        "xǁCacheHierarchyǁget_metrics__mutmut_27": xǁCacheHierarchyǁget_metrics__mutmut_27,
        "xǁCacheHierarchyǁget_metrics__mutmut_28": xǁCacheHierarchyǁget_metrics__mutmut_28,
        "xǁCacheHierarchyǁget_metrics__mutmut_29": xǁCacheHierarchyǁget_metrics__mutmut_29,
    }

    def get_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁCacheHierarchyǁget_metrics__mutmut_orig"),
            object.__getattribute__(
                self, "xǁCacheHierarchyǁget_metrics__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    get_metrics.__signature__ = _mutmut_signature(
        xǁCacheHierarchyǁget_metrics__mutmut_orig
    )
    xǁCacheHierarchyǁget_metrics__mutmut_orig.__name__ = "xǁCacheHierarchyǁget_metrics"

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


# Global cache hierarchy instance
cache_hierarchy: Optional[CacheHierarchy] = None


def x_get_cache_hierarchy__mutmut_orig() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_1() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is not None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_2() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = None
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_3() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=None,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_4() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=None,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_5() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=None,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_6() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_7() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_cleanup_interval=settings.CACHE_HIERARCHY_L2_CLEANUP_INTERVAL,
        )
    return cache_hierarchy


def x_get_cache_hierarchy__mutmut_8() -> CacheHierarchy:
    """Get or create global cache hierarchy instance."""
    global cache_hierarchy
    if cache_hierarchy is None:
        cache_hierarchy = CacheHierarchy(
            l1_max_size=settings.CACHE_HIERARCHY_L1_MAX_SIZE,
            l2_ttl_seconds=settings.CACHE_HIERARCHY_L2_TTL,
        )
    return cache_hierarchy


x_get_cache_hierarchy__mutmut_mutants: ClassVar[MutantDict] = {
    "x_get_cache_hierarchy__mutmut_1": x_get_cache_hierarchy__mutmut_1,
    "x_get_cache_hierarchy__mutmut_2": x_get_cache_hierarchy__mutmut_2,
    "x_get_cache_hierarchy__mutmut_3": x_get_cache_hierarchy__mutmut_3,
    "x_get_cache_hierarchy__mutmut_4": x_get_cache_hierarchy__mutmut_4,
    "x_get_cache_hierarchy__mutmut_5": x_get_cache_hierarchy__mutmut_5,
    "x_get_cache_hierarchy__mutmut_6": x_get_cache_hierarchy__mutmut_6,
    "x_get_cache_hierarchy__mutmut_7": x_get_cache_hierarchy__mutmut_7,
    "x_get_cache_hierarchy__mutmut_8": x_get_cache_hierarchy__mutmut_8,
}


def get_cache_hierarchy(*args, **kwargs):
    result = _mutmut_trampoline(
        x_get_cache_hierarchy__mutmut_orig,
        x_get_cache_hierarchy__mutmut_mutants,
        args,
        kwargs,
    )
    return result


get_cache_hierarchy.__signature__ = _mutmut_signature(
    x_get_cache_hierarchy__mutmut_orig
)
x_get_cache_hierarchy__mutmut_orig.__name__ = "x_get_cache_hierarchy"
