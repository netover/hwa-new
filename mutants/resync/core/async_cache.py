from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from time import time
from typing import Any, Dict, Optional

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

    def xǁAsyncTTLCacheǁ__init____mutmut_orig(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
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

    def xǁAsyncTTLCacheǁ__init____mutmut_1(
        self, ttl_seconds: int = 61, cleanup_interval: int = 30
    ):
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

    def xǁAsyncTTLCacheǁ__init____mutmut_2(
        self, ttl_seconds: int = 60, cleanup_interval: int = 31
    ):
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

    def xǁAsyncTTLCacheǁ__init____mutmut_3(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
        """
        self.ttl_seconds = None
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = asyncio.Lock()
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_4(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = None
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = asyncio.Lock()
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_5(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, CacheEntry] = None
        self.lock = asyncio.Lock()
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_6(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
        """
        Initialize the async cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            cleanup_interval: How often to run background cleanup in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.cache: Dict[str, CacheEntry] = {}
        self.lock = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_7(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
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
        self.cleanup_task: Optional[asyncio.Task] = ""
        self.is_running = False

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_8(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
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
        self.is_running = None

        # Start background cleanup task
        self._start_cleanup_task()

    def xǁAsyncTTLCacheǁ__init____mutmut_9(
        self, ttl_seconds: int = 60, cleanup_interval: int = 30
    ):
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
        self.is_running = True

        # Start background cleanup task
        self._start_cleanup_task()

    xǁAsyncTTLCacheǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁ__init____mutmut_1": xǁAsyncTTLCacheǁ__init____mutmut_1,
        "xǁAsyncTTLCacheǁ__init____mutmut_2": xǁAsyncTTLCacheǁ__init____mutmut_2,
        "xǁAsyncTTLCacheǁ__init____mutmut_3": xǁAsyncTTLCacheǁ__init____mutmut_3,
        "xǁAsyncTTLCacheǁ__init____mutmut_4": xǁAsyncTTLCacheǁ__init____mutmut_4,
        "xǁAsyncTTLCacheǁ__init____mutmut_5": xǁAsyncTTLCacheǁ__init____mutmut_5,
        "xǁAsyncTTLCacheǁ__init____mutmut_6": xǁAsyncTTLCacheǁ__init____mutmut_6,
        "xǁAsyncTTLCacheǁ__init____mutmut_7": xǁAsyncTTLCacheǁ__init____mutmut_7,
        "xǁAsyncTTLCacheǁ__init____mutmut_8": xǁAsyncTTLCacheǁ__init____mutmut_8,
        "xǁAsyncTTLCacheǁ__init____mutmut_9": xǁAsyncTTLCacheǁ__init____mutmut_9,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁ__init____mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁ__init____mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁ__init____mutmut_orig)
    xǁAsyncTTLCacheǁ__init____mutmut_orig.__name__ = "xǁAsyncTTLCacheǁ__init__"

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_orig(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_1(self) -> None:
        """Start the background cleanup task."""
        if self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_2(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = None
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_3(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = False
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_entries())

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_4(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = None

    def xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_5(self) -> None:
        """Start the background cleanup task."""
        if not self.is_running:
            self.is_running = True
            self.cleanup_task = asyncio.create_task(None)

    xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_1": xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_1,
        "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_2": xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_2,
        "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_3": xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_3,
        "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_4": xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_4,
        "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_5": xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_5,
    }

    def _start_cleanup_task(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _start_cleanup_task.__signature__ = _mutmut_signature(
        xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_orig
    )
    xǁAsyncTTLCacheǁ_start_cleanup_task__mutmut_orig.__name__ = (
        "xǁAsyncTTLCacheǁ_start_cleanup_task"
    )

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_orig(self) -> None:
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

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_1(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(None)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("AsyncTTLCache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_2(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug(None)
                break
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_3(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("XXAsyncTTLCache cleanup task cancelledXX")
                break
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_4(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("asyncttlcache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_5(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("ASYNCTTLCACHE CLEANUP TASK CANCELLED")
                break
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_6(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("AsyncTTLCache cleanup task cancelled")
                return
            except Exception as e:
                logger.error(f"Error in AsyncTTLCache cleanup task: {e}")

    async def xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_7(self) -> None:
        """Background task to cleanup expired entries."""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._remove_expired_entries()
            except asyncio.CancelledError:
                logger.debug("AsyncTTLCache cleanup task cancelled")
                break
            except Exception:
                logger.error(None)

    xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_1": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_1,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_2": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_2,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_3": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_3,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_4": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_4,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_5": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_5,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_6": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_6,
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_7": xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_7,
    }

    def _cleanup_expired_entries(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _cleanup_expired_entries.__signature__ = _mutmut_signature(
        xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_orig
    )
    xǁAsyncTTLCacheǁ_cleanup_expired_entries__mutmut_orig.__name__ = (
        "xǁAsyncTTLCacheǁ_cleanup_expired_entries"
    )

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_orig(self) -> None:
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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_1(self) -> None:
        """Remove expired entries from cache."""
        current_time = None
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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_2(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        expired_keys = None

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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_3(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        expired_keys = []

        # Find expired entries without holding the lock
        for key, entry in self.cache.items():
            if current_time + entry.timestamp > entry.ttl:
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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_4(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        expired_keys = []

        # Find expired entries without holding the lock
        for key, entry in self.cache.items():
            if current_time - entry.timestamp >= entry.ttl:
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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_5(self) -> None:
        """Remove expired entries from cache."""
        current_time = time()
        expired_keys = []

        # Find expired entries without holding the lock
        for key, entry in self.cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(None)

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

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_6(self) -> None:
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
                    if key not in self.cache:
                        del self.cache[key]
                        logger.debug(f"Removed expired cache entry: {key}")

                if expired_keys:
                    logger.debug(
                        f"Cleaned up {len(expired_keys)} expired cache entries"
                    )

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_7(self) -> None:
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
                        logger.debug(None)

                if expired_keys:
                    logger.debug(
                        f"Cleaned up {len(expired_keys)} expired cache entries"
                    )

    async def xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_8(self) -> None:
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
                    logger.debug(None)

    xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_1": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_1,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_2": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_2,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_3": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_3,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_4": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_4,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_5": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_5,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_6": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_6,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_7": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_7,
        "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_8": xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_8,
    }

    def _remove_expired_entries(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _remove_expired_entries.__signature__ = _mutmut_signature(
        xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_orig
    )
    xǁAsyncTTLCacheǁ_remove_expired_entries__mutmut_orig.__name__ = (
        "xǁAsyncTTLCacheǁ_remove_expired_entries"
    )

    async def xǁAsyncTTLCacheǁget__mutmut_orig(self, key: str) -> Any | None:
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

    async def xǁAsyncTTLCacheǁget__mutmut_1(self, key: str) -> Any | None:
        """
        Asynchronously retrieve an item from the cache.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            entry = None
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

    async def xǁAsyncTTLCacheǁget__mutmut_2(self, key: str) -> Any | None:
        """
        Asynchronously retrieve an item from the cache.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        async with self.lock:
            entry = self.cache.get(None)
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

    async def xǁAsyncTTLCacheǁget__mutmut_3(self, key: str) -> Any | None:
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
                current_time = None
                if current_time - entry.timestamp <= entry.ttl:
                    logger.debug(f"Cache HIT for key: {key}")
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")

            logger.debug(f"Cache MISS for key: {key}")
            return None

    async def xǁAsyncTTLCacheǁget__mutmut_4(self, key: str) -> Any | None:
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
                if current_time + entry.timestamp <= entry.ttl:
                    logger.debug(f"Cache HIT for key: {key}")
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")

            logger.debug(f"Cache MISS for key: {key}")
            return None

    async def xǁAsyncTTLCacheǁget__mutmut_5(self, key: str) -> Any | None:
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
                if current_time - entry.timestamp < entry.ttl:
                    logger.debug(f"Cache HIT for key: {key}")
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")

            logger.debug(f"Cache MISS for key: {key}")
            return None

    async def xǁAsyncTTLCacheǁget__mutmut_6(self, key: str) -> Any | None:
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
                    logger.debug(None)
                    return entry.data
                else:
                    # Entry expired, remove it
                    del self.cache[key]
                    logger.debug(f"Cache EXPIRED for key: {key}")

            logger.debug(f"Cache MISS for key: {key}")
            return None

    async def xǁAsyncTTLCacheǁget__mutmut_7(self, key: str) -> Any | None:
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
                    logger.debug(None)

            logger.debug(f"Cache MISS for key: {key}")
            return None

    async def xǁAsyncTTLCacheǁget__mutmut_8(self, key: str) -> Any | None:
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

            logger.debug(None)
            return None

    xǁAsyncTTLCacheǁget__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁget__mutmut_1": xǁAsyncTTLCacheǁget__mutmut_1,
        "xǁAsyncTTLCacheǁget__mutmut_2": xǁAsyncTTLCacheǁget__mutmut_2,
        "xǁAsyncTTLCacheǁget__mutmut_3": xǁAsyncTTLCacheǁget__mutmut_3,
        "xǁAsyncTTLCacheǁget__mutmut_4": xǁAsyncTTLCacheǁget__mutmut_4,
        "xǁAsyncTTLCacheǁget__mutmut_5": xǁAsyncTTLCacheǁget__mutmut_5,
        "xǁAsyncTTLCacheǁget__mutmut_6": xǁAsyncTTLCacheǁget__mutmut_6,
        "xǁAsyncTTLCacheǁget__mutmut_7": xǁAsyncTTLCacheǁget__mutmut_7,
        "xǁAsyncTTLCacheǁget__mutmut_8": xǁAsyncTTLCacheǁget__mutmut_8,
    }

    def get(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁget__mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁget__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    get.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁget__mutmut_orig)
    xǁAsyncTTLCacheǁget__mutmut_orig.__name__ = "xǁAsyncTTLCacheǁget"

    async def xǁAsyncTTLCacheǁset__mutmut_orig(
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

    async def xǁAsyncTTLCacheǁset__mutmut_1(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Asynchronously add an item to the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override for this specific entry
        """
        if ttl_seconds is not None:
            ttl_seconds = self.ttl_seconds

        current_time = time()
        entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_2(
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
            ttl_seconds = None

        current_time = time()
        entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_3(
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

        current_time = None
        entry = CacheEntry(data=value, timestamp=current_time, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_4(
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

        time()
        entry = None

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_5(
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
        entry = CacheEntry(data=None, timestamp=current_time, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_6(
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

        time()
        entry = CacheEntry(data=value, timestamp=None, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_7(
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
        entry = CacheEntry(data=value, timestamp=current_time, ttl=None)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_8(
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
        entry = CacheEntry(timestamp=current_time, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_9(
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

        time()
        entry = CacheEntry(data=value, ttl=ttl_seconds)

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_10(
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
        entry = CacheEntry(
            data=value,
            timestamp=current_time,
        )

        async with self.lock:
            self.cache[key] = entry
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_11(
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
            self.cache[key] = None
            logger.debug(f"Cache SET for key: {key}")

    async def xǁAsyncTTLCacheǁset__mutmut_12(
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
            logger.debug(None)

    xǁAsyncTTLCacheǁset__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁset__mutmut_1": xǁAsyncTTLCacheǁset__mutmut_1,
        "xǁAsyncTTLCacheǁset__mutmut_2": xǁAsyncTTLCacheǁset__mutmut_2,
        "xǁAsyncTTLCacheǁset__mutmut_3": xǁAsyncTTLCacheǁset__mutmut_3,
        "xǁAsyncTTLCacheǁset__mutmut_4": xǁAsyncTTLCacheǁset__mutmut_4,
        "xǁAsyncTTLCacheǁset__mutmut_5": xǁAsyncTTLCacheǁset__mutmut_5,
        "xǁAsyncTTLCacheǁset__mutmut_6": xǁAsyncTTLCacheǁset__mutmut_6,
        "xǁAsyncTTLCacheǁset__mutmut_7": xǁAsyncTTLCacheǁset__mutmut_7,
        "xǁAsyncTTLCacheǁset__mutmut_8": xǁAsyncTTLCacheǁset__mutmut_8,
        "xǁAsyncTTLCacheǁset__mutmut_9": xǁAsyncTTLCacheǁset__mutmut_9,
        "xǁAsyncTTLCacheǁset__mutmut_10": xǁAsyncTTLCacheǁset__mutmut_10,
        "xǁAsyncTTLCacheǁset__mutmut_11": xǁAsyncTTLCacheǁset__mutmut_11,
        "xǁAsyncTTLCacheǁset__mutmut_12": xǁAsyncTTLCacheǁset__mutmut_12,
    }

    def set(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁset__mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁset__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    set.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁset__mutmut_orig)
    xǁAsyncTTLCacheǁset__mutmut_orig.__name__ = "xǁAsyncTTLCacheǁset"

    async def xǁAsyncTTLCacheǁdelete__mutmut_orig(self, key: str) -> bool:
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

    async def xǁAsyncTTLCacheǁdelete__mutmut_1(self, key: str) -> bool:
        """
        Asynchronously delete an item from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if item was deleted, False if not found
        """
        async with self.lock:
            if key not in self.cache:
                del self.cache[key]
                logger.debug(f"Cache DELETE for key: {key}")
                return True
            return False

    async def xǁAsyncTTLCacheǁdelete__mutmut_2(self, key: str) -> bool:
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
                logger.debug(None)
                return True
            return False

    async def xǁAsyncTTLCacheǁdelete__mutmut_3(self, key: str) -> bool:
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
                return False
            return False

    async def xǁAsyncTTLCacheǁdelete__mutmut_4(self, key: str) -> bool:
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
            return True

    xǁAsyncTTLCacheǁdelete__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁdelete__mutmut_1": xǁAsyncTTLCacheǁdelete__mutmut_1,
        "xǁAsyncTTLCacheǁdelete__mutmut_2": xǁAsyncTTLCacheǁdelete__mutmut_2,
        "xǁAsyncTTLCacheǁdelete__mutmut_3": xǁAsyncTTLCacheǁdelete__mutmut_3,
        "xǁAsyncTTLCacheǁdelete__mutmut_4": xǁAsyncTTLCacheǁdelete__mutmut_4,
    }

    def delete(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁdelete__mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁdelete__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    delete.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁdelete__mutmut_orig)
    xǁAsyncTTLCacheǁdelete__mutmut_orig.__name__ = "xǁAsyncTTLCacheǁdelete"

    async def xǁAsyncTTLCacheǁclear__mutmut_orig(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug("Cache CLEARED")

    async def xǁAsyncTTLCacheǁclear__mutmut_1(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug(None)

    async def xǁAsyncTTLCacheǁclear__mutmut_2(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug("XXCache CLEAREDXX")

    async def xǁAsyncTTLCacheǁclear__mutmut_3(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug("cache cleared")

    async def xǁAsyncTTLCacheǁclear__mutmut_4(self) -> None:
        """Asynchronously clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            logger.debug("CACHE CLEARED")

    xǁAsyncTTLCacheǁclear__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁclear__mutmut_1": xǁAsyncTTLCacheǁclear__mutmut_1,
        "xǁAsyncTTLCacheǁclear__mutmut_2": xǁAsyncTTLCacheǁclear__mutmut_2,
        "xǁAsyncTTLCacheǁclear__mutmut_3": xǁAsyncTTLCacheǁclear__mutmut_3,
        "xǁAsyncTTLCacheǁclear__mutmut_4": xǁAsyncTTLCacheǁclear__mutmut_4,
    }

    def clear(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁclear__mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁclear__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    clear.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁclear__mutmut_orig)
    xǁAsyncTTLCacheǁclear__mutmut_orig.__name__ = "xǁAsyncTTLCacheǁclear"

    def size(self) -> int:
        """Get the current number of items in cache (non-async for performance)."""
        return len(self.cache)

    async def xǁAsyncTTLCacheǁstop__mutmut_orig(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_1(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = None
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_2(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = True
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_3(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task or not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_4(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("AsyncTTLCache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_5(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug(None)

    async def xǁAsyncTTLCacheǁstop__mutmut_6(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("XXAsyncTTLCache stoppedXX")

    async def xǁAsyncTTLCacheǁstop__mutmut_7(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("asyncttlcache stopped")

    async def xǁAsyncTTLCacheǁstop__mutmut_8(self) -> None:
        """Stop the background cleanup task."""
        self.is_running = False
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.debug("ASYNCTTLCACHE STOPPED")

    xǁAsyncTTLCacheǁstop__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAsyncTTLCacheǁstop__mutmut_1": xǁAsyncTTLCacheǁstop__mutmut_1,
        "xǁAsyncTTLCacheǁstop__mutmut_2": xǁAsyncTTLCacheǁstop__mutmut_2,
        "xǁAsyncTTLCacheǁstop__mutmut_3": xǁAsyncTTLCacheǁstop__mutmut_3,
        "xǁAsyncTTLCacheǁstop__mutmut_4": xǁAsyncTTLCacheǁstop__mutmut_4,
        "xǁAsyncTTLCacheǁstop__mutmut_5": xǁAsyncTTLCacheǁstop__mutmut_5,
        "xǁAsyncTTLCacheǁstop__mutmut_6": xǁAsyncTTLCacheǁstop__mutmut_6,
        "xǁAsyncTTLCacheǁstop__mutmut_7": xǁAsyncTTLCacheǁstop__mutmut_7,
        "xǁAsyncTTLCacheǁstop__mutmut_8": xǁAsyncTTLCacheǁstop__mutmut_8,
    }

    def stop(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAsyncTTLCacheǁstop__mutmut_orig"),
            object.__getattribute__(self, "xǁAsyncTTLCacheǁstop__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    stop.__signature__ = _mutmut_signature(xǁAsyncTTLCacheǁstop__mutmut_orig)
    xǁAsyncTTLCacheǁstop__mutmut_orig.__name__ = "xǁAsyncTTLCacheǁstop"

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.stop()
