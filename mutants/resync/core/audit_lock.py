"""
Distributed Audit Lock for Resync

This module provides a dedicated distributed locking mechanism for audit operations
to prevent race conditions during concurrent memory processing.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional, cast

from redis.asyncio import Redis as AsyncRedis

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


class DistributedAuditLock:
    """
    A distributed lock implementation using Redis for audit operations.

    This class provides atomic locking to prevent race conditions when multiple
    IA Auditor processes attempt to process the same memory simultaneously.
    """

    def xǁDistributedAuditLockǁ__init____mutmut_orig(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_1(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = None
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_2(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(None)
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_3(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            and "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_4(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            and getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_5(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(None, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_6(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, None, "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_7(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", None)
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_8(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr("REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_9(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_10(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(
                settings,
                "REDIS_URL",
            )
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_11(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "XXREDIS_URLXX", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_12(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "redis_url", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_13(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "XXredis://localhost:6379/1XX")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_14(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "REDIS://LOCALHOST:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_15(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "XXredis://localhost:6379/1XX"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_16(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "REDIS://LOCALHOST:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_17(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = ""
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_18(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = None
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_19(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "XXaudit_lockXX"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_20(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "AUDIT_LOCK"
        self.release_script_sha: Optional[str] = None

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_21(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = ""

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    def xǁDistributedAuditLockǁ__init____mutmut_22(
        self, redis_url: Optional[str] = None
    ) -> None:
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url: str = str(
            redis_url
            or getattr(settings, "REDIS_URL", "redis://localhost:6379/1")
            or "redis://localhost:6379/1"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix: str = "audit_lock"
        self.release_script_sha: Optional[str] = None

        logger.info(None)

    xǁDistributedAuditLockǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁ__init____mutmut_1": xǁDistributedAuditLockǁ__init____mutmut_1,
        "xǁDistributedAuditLockǁ__init____mutmut_2": xǁDistributedAuditLockǁ__init____mutmut_2,
        "xǁDistributedAuditLockǁ__init____mutmut_3": xǁDistributedAuditLockǁ__init____mutmut_3,
        "xǁDistributedAuditLockǁ__init____mutmut_4": xǁDistributedAuditLockǁ__init____mutmut_4,
        "xǁDistributedAuditLockǁ__init____mutmut_5": xǁDistributedAuditLockǁ__init____mutmut_5,
        "xǁDistributedAuditLockǁ__init____mutmut_6": xǁDistributedAuditLockǁ__init____mutmut_6,
        "xǁDistributedAuditLockǁ__init____mutmut_7": xǁDistributedAuditLockǁ__init____mutmut_7,
        "xǁDistributedAuditLockǁ__init____mutmut_8": xǁDistributedAuditLockǁ__init____mutmut_8,
        "xǁDistributedAuditLockǁ__init____mutmut_9": xǁDistributedAuditLockǁ__init____mutmut_9,
        "xǁDistributedAuditLockǁ__init____mutmut_10": xǁDistributedAuditLockǁ__init____mutmut_10,
        "xǁDistributedAuditLockǁ__init____mutmut_11": xǁDistributedAuditLockǁ__init____mutmut_11,
        "xǁDistributedAuditLockǁ__init____mutmut_12": xǁDistributedAuditLockǁ__init____mutmut_12,
        "xǁDistributedAuditLockǁ__init____mutmut_13": xǁDistributedAuditLockǁ__init____mutmut_13,
        "xǁDistributedAuditLockǁ__init____mutmut_14": xǁDistributedAuditLockǁ__init____mutmut_14,
        "xǁDistributedAuditLockǁ__init____mutmut_15": xǁDistributedAuditLockǁ__init____mutmut_15,
        "xǁDistributedAuditLockǁ__init____mutmut_16": xǁDistributedAuditLockǁ__init____mutmut_16,
        "xǁDistributedAuditLockǁ__init____mutmut_17": xǁDistributedAuditLockǁ__init____mutmut_17,
        "xǁDistributedAuditLockǁ__init____mutmut_18": xǁDistributedAuditLockǁ__init____mutmut_18,
        "xǁDistributedAuditLockǁ__init____mutmut_19": xǁDistributedAuditLockǁ__init____mutmut_19,
        "xǁDistributedAuditLockǁ__init____mutmut_20": xǁDistributedAuditLockǁ__init____mutmut_20,
        "xǁDistributedAuditLockǁ__init____mutmut_21": xǁDistributedAuditLockǁ__init____mutmut_21,
        "xǁDistributedAuditLockǁ__init____mutmut_22": xǁDistributedAuditLockǁ__init____mutmut_22,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁ__init____mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁ__init____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁ__init____mutmut_orig
    )
    xǁDistributedAuditLockǁ__init____mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁ__init__"
    )

    async def xǁDistributedAuditLockǁconnect__mutmut_orig(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_1(self) -> None:
        """Initialize Redis connection."""
        if self.client is not None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_2(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = None
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_3(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(None)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_4(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = None
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_5(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = None
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_6(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(None)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_7(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info(None)

    async def xǁDistributedAuditLockǁconnect__mutmut_8(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("XXDistributedAuditLock connected to RedisXX")

    async def xǁDistributedAuditLockǁconnect__mutmut_9(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("distributedauditlock connected to redis")

    async def xǁDistributedAuditLockǁconnect__mutmut_10(self) -> None:
        """Initialize Redis connection."""
        if self.client is None:
            self.client = AsyncRedis.from_url(self.redis_url)
            # Load Lua script on connection
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.release_script_sha = await self.client.script_load(lua_script)
            # Test connection
            await self.client.ping()
            logger.info("DISTRIBUTEDAUDITLOCK CONNECTED TO REDIS")

    xǁDistributedAuditLockǁconnect__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁconnect__mutmut_1": xǁDistributedAuditLockǁconnect__mutmut_1,
        "xǁDistributedAuditLockǁconnect__mutmut_2": xǁDistributedAuditLockǁconnect__mutmut_2,
        "xǁDistributedAuditLockǁconnect__mutmut_3": xǁDistributedAuditLockǁconnect__mutmut_3,
        "xǁDistributedAuditLockǁconnect__mutmut_4": xǁDistributedAuditLockǁconnect__mutmut_4,
        "xǁDistributedAuditLockǁconnect__mutmut_5": xǁDistributedAuditLockǁconnect__mutmut_5,
        "xǁDistributedAuditLockǁconnect__mutmut_6": xǁDistributedAuditLockǁconnect__mutmut_6,
        "xǁDistributedAuditLockǁconnect__mutmut_7": xǁDistributedAuditLockǁconnect__mutmut_7,
        "xǁDistributedAuditLockǁconnect__mutmut_8": xǁDistributedAuditLockǁconnect__mutmut_8,
        "xǁDistributedAuditLockǁconnect__mutmut_9": xǁDistributedAuditLockǁconnect__mutmut_9,
        "xǁDistributedAuditLockǁconnect__mutmut_10": xǁDistributedAuditLockǁconnect__mutmut_10,
    }

    def connect(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁconnect__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁconnect__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    connect.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁconnect__mutmut_orig
    )
    xǁDistributedAuditLockǁconnect__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁconnect"
    )

    async def xǁDistributedAuditLockǁdisconnect__mutmut_orig(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("DistributedAuditLock disconnected from Redis")

    async def xǁDistributedAuditLockǁdisconnect__mutmut_1(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = ""
            logger.info("DistributedAuditLock disconnected from Redis")

    async def xǁDistributedAuditLockǁdisconnect__mutmut_2(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info(None)

    async def xǁDistributedAuditLockǁdisconnect__mutmut_3(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("XXDistributedAuditLock disconnected from RedisXX")

    async def xǁDistributedAuditLockǁdisconnect__mutmut_4(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("distributedauditlock disconnected from redis")

    async def xǁDistributedAuditLockǁdisconnect__mutmut_5(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("DISTRIBUTEDAUDITLOCK DISCONNECTED FROM REDIS")

    xǁDistributedAuditLockǁdisconnect__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁdisconnect__mutmut_1": xǁDistributedAuditLockǁdisconnect__mutmut_1,
        "xǁDistributedAuditLockǁdisconnect__mutmut_2": xǁDistributedAuditLockǁdisconnect__mutmut_2,
        "xǁDistributedAuditLockǁdisconnect__mutmut_3": xǁDistributedAuditLockǁdisconnect__mutmut_3,
        "xǁDistributedAuditLockǁdisconnect__mutmut_4": xǁDistributedAuditLockǁdisconnect__mutmut_4,
        "xǁDistributedAuditLockǁdisconnect__mutmut_5": xǁDistributedAuditLockǁdisconnect__mutmut_5,
    }

    def disconnect(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁdisconnect__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁdisconnect__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    disconnect.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁdisconnect__mutmut_orig
    )
    xǁDistributedAuditLockǁdisconnect__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁdisconnect"
    )

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_orig(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError("Invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_1(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) and len(memory_id) == 0:
            raise ValueError("Invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_2(self, memory_id: str) -> str:
        if isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError("Invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_3(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) != 0:
            raise ValueError("Invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_4(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 1:
            raise ValueError("Invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_5(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError(None)
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_6(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError("XXInvalid memory_id - must be a non-empty stringXX")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_7(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError("invalid memory_id - must be a non-empty string")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    def xǁDistributedAuditLockǁ_get_lock_key__mutmut_8(self, memory_id: str) -> str:
        if not isinstance(memory_id, str) or len(memory_id) == 0:
            raise ValueError("INVALID MEMORY_ID - MUST BE A NON-EMPTY STRING")
        """
        Generate a unique lock key for a memory ID.

        Args:
            memory_id: The memory ID to generate a lock key for.

        Returns:
            A unique lock key string.
        """
        return f"{self._lock_prefix}:{memory_id}"

    xǁDistributedAuditLockǁ_get_lock_key__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_1": xǁDistributedAuditLockǁ_get_lock_key__mutmut_1,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_2": xǁDistributedAuditLockǁ_get_lock_key__mutmut_2,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_3": xǁDistributedAuditLockǁ_get_lock_key__mutmut_3,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_4": xǁDistributedAuditLockǁ_get_lock_key__mutmut_4,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_5": xǁDistributedAuditLockǁ_get_lock_key__mutmut_5,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_6": xǁDistributedAuditLockǁ_get_lock_key__mutmut_6,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_7": xǁDistributedAuditLockǁ_get_lock_key__mutmut_7,
        "xǁDistributedAuditLockǁ_get_lock_key__mutmut_8": xǁDistributedAuditLockǁ_get_lock_key__mutmut_8,
    }

    def _get_lock_key(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁ_get_lock_key__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁ_get_lock_key__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _get_lock_key.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁ_get_lock_key__mutmut_orig
    )
    xǁDistributedAuditLockǁ_get_lock_key__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁ_get_lock_key"
    )

    async def xǁDistributedAuditLockǁacquire__mutmut_orig(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_1(
        self, memory_id: str, timeout: int = 6
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_2(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is not None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_3(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = None

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_4(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(None, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_5(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, None)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_6(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_7(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(
            AsyncRedis,
        )

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_8(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = None
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_9(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(None)
        return AuditLockContext(self.client, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_10(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(None, lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_11(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        return AuditLockContext(self.client, None, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_12(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, None, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_13(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout, None)

    async def xǁDistributedAuditLockǁacquire__mutmut_14(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(lock_key, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_15(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        return AuditLockContext(self.client, timeout, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_16(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, self.release_script_sha)

    async def xǁDistributedAuditLockǁacquire__mutmut_17(
        self, memory_id: str, timeout: int = 5
    ) -> "AuditLockContext":
        """
        Acquire a distributed lock for a memory ID.

        Args:
            memory_id: The memory ID to lock.
            timeout: Lock timeout in seconds.

        Returns:
            An AuditLockContext instance.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(
            self.client,
            lock_key,
            timeout,
        )

    xǁDistributedAuditLockǁacquire__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁacquire__mutmut_1": xǁDistributedAuditLockǁacquire__mutmut_1,
        "xǁDistributedAuditLockǁacquire__mutmut_2": xǁDistributedAuditLockǁacquire__mutmut_2,
        "xǁDistributedAuditLockǁacquire__mutmut_3": xǁDistributedAuditLockǁacquire__mutmut_3,
        "xǁDistributedAuditLockǁacquire__mutmut_4": xǁDistributedAuditLockǁacquire__mutmut_4,
        "xǁDistributedAuditLockǁacquire__mutmut_5": xǁDistributedAuditLockǁacquire__mutmut_5,
        "xǁDistributedAuditLockǁacquire__mutmut_6": xǁDistributedAuditLockǁacquire__mutmut_6,
        "xǁDistributedAuditLockǁacquire__mutmut_7": xǁDistributedAuditLockǁacquire__mutmut_7,
        "xǁDistributedAuditLockǁacquire__mutmut_8": xǁDistributedAuditLockǁacquire__mutmut_8,
        "xǁDistributedAuditLockǁacquire__mutmut_9": xǁDistributedAuditLockǁacquire__mutmut_9,
        "xǁDistributedAuditLockǁacquire__mutmut_10": xǁDistributedAuditLockǁacquire__mutmut_10,
        "xǁDistributedAuditLockǁacquire__mutmut_11": xǁDistributedAuditLockǁacquire__mutmut_11,
        "xǁDistributedAuditLockǁacquire__mutmut_12": xǁDistributedAuditLockǁacquire__mutmut_12,
        "xǁDistributedAuditLockǁacquire__mutmut_13": xǁDistributedAuditLockǁacquire__mutmut_13,
        "xǁDistributedAuditLockǁacquire__mutmut_14": xǁDistributedAuditLockǁacquire__mutmut_14,
        "xǁDistributedAuditLockǁacquire__mutmut_15": xǁDistributedAuditLockǁacquire__mutmut_15,
        "xǁDistributedAuditLockǁacquire__mutmut_16": xǁDistributedAuditLockǁacquire__mutmut_16,
        "xǁDistributedAuditLockǁacquire__mutmut_17": xǁDistributedAuditLockǁacquire__mutmut_17,
    }

    def acquire(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁacquire__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁacquire__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    acquire.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁacquire__mutmut_orig
    )
    xǁDistributedAuditLockǁacquire__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁacquire"
    )

    async def xǁDistributedAuditLockǁis_locked__mutmut_orig(
        self, memory_id: str
    ) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_1(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is not None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_2(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = None

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_3(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(None, self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_4(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, None)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_5(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_6(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(
            AsyncRedis,
        )

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_7(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = None
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_8(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(None)
        return int(await self.client.exists(lock_key)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_9(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        return int(None) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_10(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        return int(await self.client.exists(None)) == 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_11(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) != 1

    async def xǁDistributedAuditLockǁis_locked__mutmut_12(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        return int(await self.client.exists(lock_key)) == 2

    xǁDistributedAuditLockǁis_locked__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁis_locked__mutmut_1": xǁDistributedAuditLockǁis_locked__mutmut_1,
        "xǁDistributedAuditLockǁis_locked__mutmut_2": xǁDistributedAuditLockǁis_locked__mutmut_2,
        "xǁDistributedAuditLockǁis_locked__mutmut_3": xǁDistributedAuditLockǁis_locked__mutmut_3,
        "xǁDistributedAuditLockǁis_locked__mutmut_4": xǁDistributedAuditLockǁis_locked__mutmut_4,
        "xǁDistributedAuditLockǁis_locked__mutmut_5": xǁDistributedAuditLockǁis_locked__mutmut_5,
        "xǁDistributedAuditLockǁis_locked__mutmut_6": xǁDistributedAuditLockǁis_locked__mutmut_6,
        "xǁDistributedAuditLockǁis_locked__mutmut_7": xǁDistributedAuditLockǁis_locked__mutmut_7,
        "xǁDistributedAuditLockǁis_locked__mutmut_8": xǁDistributedAuditLockǁis_locked__mutmut_8,
        "xǁDistributedAuditLockǁis_locked__mutmut_9": xǁDistributedAuditLockǁis_locked__mutmut_9,
        "xǁDistributedAuditLockǁis_locked__mutmut_10": xǁDistributedAuditLockǁis_locked__mutmut_10,
        "xǁDistributedAuditLockǁis_locked__mutmut_11": xǁDistributedAuditLockǁis_locked__mutmut_11,
        "xǁDistributedAuditLockǁis_locked__mutmut_12": xǁDistributedAuditLockǁis_locked__mutmut_12,
    }

    def is_locked(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁis_locked__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁis_locked__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    is_locked.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁis_locked__mutmut_orig
    )
    xǁDistributedAuditLockǁis_locked__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁis_locked"
    )

    async def xǁDistributedAuditLockǁforce_release__mutmut_orig(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_1(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is not None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_2(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = None

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_3(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(None, self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_4(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, None)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_5(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_6(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(
            AsyncRedis,
        )

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_7(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = None
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_8(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(None)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_9(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        result = None
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_10(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        self._get_lock_key(memory_id)
        result = await self.client.delete(None)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_11(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(None)
        return bool(result)

    async def xǁDistributedAuditLockǁforce_release__mutmut_12(
        self, memory_id: str
    ) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(None)

    xǁDistributedAuditLockǁforce_release__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁDistributedAuditLockǁforce_release__mutmut_1": xǁDistributedAuditLockǁforce_release__mutmut_1,
        "xǁDistributedAuditLockǁforce_release__mutmut_2": xǁDistributedAuditLockǁforce_release__mutmut_2,
        "xǁDistributedAuditLockǁforce_release__mutmut_3": xǁDistributedAuditLockǁforce_release__mutmut_3,
        "xǁDistributedAuditLockǁforce_release__mutmut_4": xǁDistributedAuditLockǁforce_release__mutmut_4,
        "xǁDistributedAuditLockǁforce_release__mutmut_5": xǁDistributedAuditLockǁforce_release__mutmut_5,
        "xǁDistributedAuditLockǁforce_release__mutmut_6": xǁDistributedAuditLockǁforce_release__mutmut_6,
        "xǁDistributedAuditLockǁforce_release__mutmut_7": xǁDistributedAuditLockǁforce_release__mutmut_7,
        "xǁDistributedAuditLockǁforce_release__mutmut_8": xǁDistributedAuditLockǁforce_release__mutmut_8,
        "xǁDistributedAuditLockǁforce_release__mutmut_9": xǁDistributedAuditLockǁforce_release__mutmut_9,
        "xǁDistributedAuditLockǁforce_release__mutmut_10": xǁDistributedAuditLockǁforce_release__mutmut_10,
        "xǁDistributedAuditLockǁforce_release__mutmut_11": xǁDistributedAuditLockǁforce_release__mutmut_11,
        "xǁDistributedAuditLockǁforce_release__mutmut_12": xǁDistributedAuditLockǁforce_release__mutmut_12,
    }

    def force_release(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁforce_release__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁforce_release__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    force_release.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁforce_release__mutmut_orig
    )
    xǁDistributedAuditLockǁforce_release__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁforce_release"
    )

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_orig(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_1(
        self, max_age: int = 61
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_2(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is not None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_3(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = None

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_4(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(None, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_5(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, None)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_6(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_7(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(
            AsyncRedis,
        )

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_8(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = None

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_9(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 1

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_10(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = None
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_11(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = None

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_12(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(None)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_13(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = None

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_14(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode(None)

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_15(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("XXutf-8XX")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_16(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("UTF-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_17(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = None
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_18(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(None)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_19(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None and ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_20(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is not None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_21(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl >= max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_22(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(None)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_23(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count = 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_24(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count -= 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_25(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 2

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_26(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count >= 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_27(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 1:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_28(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(None)

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_29(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception:
            logger.error(None)
            return 0

    async def xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_30(
        self, max_age: int = 60
    ) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        self.client = cast(AsyncRedis, self.client)

        try:
            cleaned_count: int = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl is None or ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 1

    xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_mutants: ClassVar[
        MutantDict
    ] = {
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_1": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_1,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_2": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_2,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_3": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_3,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_4": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_4,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_5": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_5,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_6": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_6,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_7": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_7,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_8": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_8,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_9": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_9,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_10": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_10,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_11": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_11,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_12": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_12,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_13": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_13,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_14": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_14,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_15": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_15,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_16": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_16,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_17": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_17,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_18": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_18,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_19": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_19,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_20": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_20,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_21": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_21,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_22": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_22,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_23": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_23,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_24": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_24,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_25": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_25,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_26": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_26,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_27": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_27,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_28": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_28,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_29": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_29,
        "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_30": xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_30,
    }

    def cleanup_expired_locks(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    cleanup_expired_locks.__signature__ = _mutmut_signature(
        xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_orig
    )
    xǁDistributedAuditLockǁcleanup_expired_locks__mutmut_orig.__name__ = (
        "xǁDistributedAuditLockǁcleanup_expired_locks"
    )


class AuditLockContext:
    """
    Context manager for distributed audit locks.

    Usage:
        async with audit_lock.acquire(memory_id, timeout=5):
            # Critical section - memory processing
            pass
    """

    def xǁAuditLockContextǁ__init____mutmut_orig(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = False
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_1(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = None
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = False
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_2(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = None
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = False
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_3(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = None
        self.lock_value: Optional[str] = None
        self._locked: bool = False
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_4(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = ""
        self._locked: bool = False
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_5(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = None
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_6(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = True
        self.release_script_sha: Optional[str] = release_script_sha

    def xǁAuditLockContextǁ__init____mutmut_7(
        self,
        client: AsyncRedis,
        lock_key: str,
        timeout: int,
        release_script_sha: Optional[str] = None,
    ) -> None:
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client: AsyncRedis = client
        self.lock_key: str = lock_key
        self.timeout: int = timeout
        self.lock_value: Optional[str] = None
        self._locked: bool = False
        self.release_script_sha: Optional[str] = None

    xǁAuditLockContextǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAuditLockContextǁ__init____mutmut_1": xǁAuditLockContextǁ__init____mutmut_1,
        "xǁAuditLockContextǁ__init____mutmut_2": xǁAuditLockContextǁ__init____mutmut_2,
        "xǁAuditLockContextǁ__init____mutmut_3": xǁAuditLockContextǁ__init____mutmut_3,
        "xǁAuditLockContextǁ__init____mutmut_4": xǁAuditLockContextǁ__init____mutmut_4,
        "xǁAuditLockContextǁ__init____mutmut_5": xǁAuditLockContextǁ__init____mutmut_5,
        "xǁAuditLockContextǁ__init____mutmut_6": xǁAuditLockContextǁ__init____mutmut_6,
        "xǁAuditLockContextǁ__init____mutmut_7": xǁAuditLockContextǁ__init____mutmut_7,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAuditLockContextǁ__init____mutmut_orig"),
            object.__getattribute__(
                self, "xǁAuditLockContextǁ__init____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁAuditLockContextǁ__init____mutmut_orig)
    xǁAuditLockContextǁ__init____mutmut_orig.__name__ = "xǁAuditLockContextǁ__init__"

    async def xǁAuditLockContextǁ__aenter____mutmut_orig(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_1(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = None

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_2(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(None)

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_3(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = None

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_4(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            None,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_5(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            None,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_6(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=None,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_7(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=None,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_8(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_9(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_10(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_11(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_12(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=False,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_13(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout / 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_14(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1001,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_15(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = None
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_16(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = False
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_17(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(None)
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def xǁAuditLockContextǁ__aenter____mutmut_18(self) -> "AuditLockContext":
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

        if success:
            self._locked = True
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(None)

    xǁAuditLockContextǁ__aenter____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAuditLockContextǁ__aenter____mutmut_1": xǁAuditLockContextǁ__aenter____mutmut_1,
        "xǁAuditLockContextǁ__aenter____mutmut_2": xǁAuditLockContextǁ__aenter____mutmut_2,
        "xǁAuditLockContextǁ__aenter____mutmut_3": xǁAuditLockContextǁ__aenter____mutmut_3,
        "xǁAuditLockContextǁ__aenter____mutmut_4": xǁAuditLockContextǁ__aenter____mutmut_4,
        "xǁAuditLockContextǁ__aenter____mutmut_5": xǁAuditLockContextǁ__aenter____mutmut_5,
        "xǁAuditLockContextǁ__aenter____mutmut_6": xǁAuditLockContextǁ__aenter____mutmut_6,
        "xǁAuditLockContextǁ__aenter____mutmut_7": xǁAuditLockContextǁ__aenter____mutmut_7,
        "xǁAuditLockContextǁ__aenter____mutmut_8": xǁAuditLockContextǁ__aenter____mutmut_8,
        "xǁAuditLockContextǁ__aenter____mutmut_9": xǁAuditLockContextǁ__aenter____mutmut_9,
        "xǁAuditLockContextǁ__aenter____mutmut_10": xǁAuditLockContextǁ__aenter____mutmut_10,
        "xǁAuditLockContextǁ__aenter____mutmut_11": xǁAuditLockContextǁ__aenter____mutmut_11,
        "xǁAuditLockContextǁ__aenter____mutmut_12": xǁAuditLockContextǁ__aenter____mutmut_12,
        "xǁAuditLockContextǁ__aenter____mutmut_13": xǁAuditLockContextǁ__aenter____mutmut_13,
        "xǁAuditLockContextǁ__aenter____mutmut_14": xǁAuditLockContextǁ__aenter____mutmut_14,
        "xǁAuditLockContextǁ__aenter____mutmut_15": xǁAuditLockContextǁ__aenter____mutmut_15,
        "xǁAuditLockContextǁ__aenter____mutmut_16": xǁAuditLockContextǁ__aenter____mutmut_16,
        "xǁAuditLockContextǁ__aenter____mutmut_17": xǁAuditLockContextǁ__aenter____mutmut_17,
        "xǁAuditLockContextǁ__aenter____mutmut_18": xǁAuditLockContextǁ__aenter____mutmut_18,
    }

    def __aenter__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAuditLockContextǁ__aenter____mutmut_orig"),
            object.__getattribute__(
                self, "xǁAuditLockContextǁ__aenter____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __aenter__.__signature__ = _mutmut_signature(
        xǁAuditLockContextǁ__aenter____mutmut_orig
    )
    xǁAuditLockContextǁ__aenter____mutmut_orig.__name__ = (
        "xǁAuditLockContextǁ__aenter__"
    )

    async def xǁAuditLockContextǁ__aexit____mutmut_orig(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Release the lock."""
        if self._locked and self.lock_value:
            await self._release_lock()

    async def xǁAuditLockContextǁ__aexit____mutmut_1(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Release the lock."""
        if self._locked or self.lock_value:
            await self._release_lock()

    xǁAuditLockContextǁ__aexit____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAuditLockContextǁ__aexit____mutmut_1": xǁAuditLockContextǁ__aexit____mutmut_1
    }

    def __aexit__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAuditLockContextǁ__aexit____mutmut_orig"),
            object.__getattribute__(
                self, "xǁAuditLockContextǁ__aexit____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __aexit__.__signature__ = _mutmut_signature(
        xǁAuditLockContextǁ__aexit____mutmut_orig
    )
    xǁAuditLockContextǁ__aexit____mutmut_orig.__name__ = "xǁAuditLockContextǁ__aexit__"

    async def xǁAuditLockContextǁ_release_lock__mutmut_orig(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_1(self) -> None:
        """Release the lock if owned by this instance."""
        if self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_2(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) and len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_3(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_4(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) != 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_5(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 1:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_6(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError(None)

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_7(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("XXInvalid lock key format - must be non-empty stringXX")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_8(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_9(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("INVALID LOCK KEY FORMAT - MUST BE NON-EMPTY STRING")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_10(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            and not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_11(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            and len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_12(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_13(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) == 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_14(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 37
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_15(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_16(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count(None) == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_17(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("XX-XX") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_18(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") != 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_19(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 5
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_20(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError(None)

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_21(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("XXInvalid lock value (must be a UUID)XX")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_22(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("invalid lock value (must be a uuid)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_23(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("INVALID LOCK VALUE (MUST BE A UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_24(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = None
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_25(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    None, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_26(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, None, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_27(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, None, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_28(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, None
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_29(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_30(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_31(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_32(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha,
                    1,
                    self.lock_key,
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_33(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 2, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_34(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning(None)
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_35(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("XXUsing eval fallback - script not loadedXX")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_36(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_37(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("USING EVAL FALLBACK - SCRIPT NOT LOADED")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_38(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = None
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_39(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = None

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_40(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    None, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_41(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, None, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_42(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, None, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_43(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(lua_script, 1, self.lock_key, None)

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_44(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(1, self.lock_key, self.lock_value)

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_45(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_46(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(lua_script, 1, self.lock_value)

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_47(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script,
                    1,
                    self.lock_key,
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_48(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 2, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_49(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result != 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_50(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 2:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_51(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(None)
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_52(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(None)

        except Exception as e:
            logger.error(f"Error executing Redis script during lock release: {str(e)}")
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_53(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception:
            logger.error(None)
            raise

    async def xǁAuditLockContextǁ_release_lock__mutmut_54(self) -> None:
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Validate lock key and value
        if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
            raise ValueError("Invalid lock key format - must be non-empty string")

        if (
            not isinstance(self.lock_value, str)
            or len(self.lock_value) != 36
            or not self.lock_value.count("-") == 4
        ):
            raise ValueError("Invalid lock value (must be a UUID)")

        try:
            # Use EVALSHA for atomic check-and-delete
            if self.release_script_sha:
                result: int = await self.client.evalsha(
                    self.release_script_sha, 1, self.lock_key, self.lock_value
                )
            else:
                # Fallback to eval if script not loaded
                logger.warning("Using eval fallback - script not loaded")
                lua_script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
                """
                result: int = await self.client.eval(
                    lua_script, 1, self.lock_key, self.lock_value
                )

            if result == 1:
                logger.debug(f"Released audit lock: {self.lock_key}")
            else:
                logger.warning(
                    f"Failed to release audit lock: {self.lock_key} (may have expired)"
                )

        except Exception:
            logger.error(
                f"Error executing Redis script during lock release: {str(None)}"
            )
            raise

    xǁAuditLockContextǁ_release_lock__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAuditLockContextǁ_release_lock__mutmut_1": xǁAuditLockContextǁ_release_lock__mutmut_1,
        "xǁAuditLockContextǁ_release_lock__mutmut_2": xǁAuditLockContextǁ_release_lock__mutmut_2,
        "xǁAuditLockContextǁ_release_lock__mutmut_3": xǁAuditLockContextǁ_release_lock__mutmut_3,
        "xǁAuditLockContextǁ_release_lock__mutmut_4": xǁAuditLockContextǁ_release_lock__mutmut_4,
        "xǁAuditLockContextǁ_release_lock__mutmut_5": xǁAuditLockContextǁ_release_lock__mutmut_5,
        "xǁAuditLockContextǁ_release_lock__mutmut_6": xǁAuditLockContextǁ_release_lock__mutmut_6,
        "xǁAuditLockContextǁ_release_lock__mutmut_7": xǁAuditLockContextǁ_release_lock__mutmut_7,
        "xǁAuditLockContextǁ_release_lock__mutmut_8": xǁAuditLockContextǁ_release_lock__mutmut_8,
        "xǁAuditLockContextǁ_release_lock__mutmut_9": xǁAuditLockContextǁ_release_lock__mutmut_9,
        "xǁAuditLockContextǁ_release_lock__mutmut_10": xǁAuditLockContextǁ_release_lock__mutmut_10,
        "xǁAuditLockContextǁ_release_lock__mutmut_11": xǁAuditLockContextǁ_release_lock__mutmut_11,
        "xǁAuditLockContextǁ_release_lock__mutmut_12": xǁAuditLockContextǁ_release_lock__mutmut_12,
        "xǁAuditLockContextǁ_release_lock__mutmut_13": xǁAuditLockContextǁ_release_lock__mutmut_13,
        "xǁAuditLockContextǁ_release_lock__mutmut_14": xǁAuditLockContextǁ_release_lock__mutmut_14,
        "xǁAuditLockContextǁ_release_lock__mutmut_15": xǁAuditLockContextǁ_release_lock__mutmut_15,
        "xǁAuditLockContextǁ_release_lock__mutmut_16": xǁAuditLockContextǁ_release_lock__mutmut_16,
        "xǁAuditLockContextǁ_release_lock__mutmut_17": xǁAuditLockContextǁ_release_lock__mutmut_17,
        "xǁAuditLockContextǁ_release_lock__mutmut_18": xǁAuditLockContextǁ_release_lock__mutmut_18,
        "xǁAuditLockContextǁ_release_lock__mutmut_19": xǁAuditLockContextǁ_release_lock__mutmut_19,
        "xǁAuditLockContextǁ_release_lock__mutmut_20": xǁAuditLockContextǁ_release_lock__mutmut_20,
        "xǁAuditLockContextǁ_release_lock__mutmut_21": xǁAuditLockContextǁ_release_lock__mutmut_21,
        "xǁAuditLockContextǁ_release_lock__mutmut_22": xǁAuditLockContextǁ_release_lock__mutmut_22,
        "xǁAuditLockContextǁ_release_lock__mutmut_23": xǁAuditLockContextǁ_release_lock__mutmut_23,
        "xǁAuditLockContextǁ_release_lock__mutmut_24": xǁAuditLockContextǁ_release_lock__mutmut_24,
        "xǁAuditLockContextǁ_release_lock__mutmut_25": xǁAuditLockContextǁ_release_lock__mutmut_25,
        "xǁAuditLockContextǁ_release_lock__mutmut_26": xǁAuditLockContextǁ_release_lock__mutmut_26,
        "xǁAuditLockContextǁ_release_lock__mutmut_27": xǁAuditLockContextǁ_release_lock__mutmut_27,
        "xǁAuditLockContextǁ_release_lock__mutmut_28": xǁAuditLockContextǁ_release_lock__mutmut_28,
        "xǁAuditLockContextǁ_release_lock__mutmut_29": xǁAuditLockContextǁ_release_lock__mutmut_29,
        "xǁAuditLockContextǁ_release_lock__mutmut_30": xǁAuditLockContextǁ_release_lock__mutmut_30,
        "xǁAuditLockContextǁ_release_lock__mutmut_31": xǁAuditLockContextǁ_release_lock__mutmut_31,
        "xǁAuditLockContextǁ_release_lock__mutmut_32": xǁAuditLockContextǁ_release_lock__mutmut_32,
        "xǁAuditLockContextǁ_release_lock__mutmut_33": xǁAuditLockContextǁ_release_lock__mutmut_33,
        "xǁAuditLockContextǁ_release_lock__mutmut_34": xǁAuditLockContextǁ_release_lock__mutmut_34,
        "xǁAuditLockContextǁ_release_lock__mutmut_35": xǁAuditLockContextǁ_release_lock__mutmut_35,
        "xǁAuditLockContextǁ_release_lock__mutmut_36": xǁAuditLockContextǁ_release_lock__mutmut_36,
        "xǁAuditLockContextǁ_release_lock__mutmut_37": xǁAuditLockContextǁ_release_lock__mutmut_37,
        "xǁAuditLockContextǁ_release_lock__mutmut_38": xǁAuditLockContextǁ_release_lock__mutmut_38,
        "xǁAuditLockContextǁ_release_lock__mutmut_39": xǁAuditLockContextǁ_release_lock__mutmut_39,
        "xǁAuditLockContextǁ_release_lock__mutmut_40": xǁAuditLockContextǁ_release_lock__mutmut_40,
        "xǁAuditLockContextǁ_release_lock__mutmut_41": xǁAuditLockContextǁ_release_lock__mutmut_41,
        "xǁAuditLockContextǁ_release_lock__mutmut_42": xǁAuditLockContextǁ_release_lock__mutmut_42,
        "xǁAuditLockContextǁ_release_lock__mutmut_43": xǁAuditLockContextǁ_release_lock__mutmut_43,
        "xǁAuditLockContextǁ_release_lock__mutmut_44": xǁAuditLockContextǁ_release_lock__mutmut_44,
        "xǁAuditLockContextǁ_release_lock__mutmut_45": xǁAuditLockContextǁ_release_lock__mutmut_45,
        "xǁAuditLockContextǁ_release_lock__mutmut_46": xǁAuditLockContextǁ_release_lock__mutmut_46,
        "xǁAuditLockContextǁ_release_lock__mutmut_47": xǁAuditLockContextǁ_release_lock__mutmut_47,
        "xǁAuditLockContextǁ_release_lock__mutmut_48": xǁAuditLockContextǁ_release_lock__mutmut_48,
        "xǁAuditLockContextǁ_release_lock__mutmut_49": xǁAuditLockContextǁ_release_lock__mutmut_49,
        "xǁAuditLockContextǁ_release_lock__mutmut_50": xǁAuditLockContextǁ_release_lock__mutmut_50,
        "xǁAuditLockContextǁ_release_lock__mutmut_51": xǁAuditLockContextǁ_release_lock__mutmut_51,
        "xǁAuditLockContextǁ_release_lock__mutmut_52": xǁAuditLockContextǁ_release_lock__mutmut_52,
        "xǁAuditLockContextǁ_release_lock__mutmut_53": xǁAuditLockContextǁ_release_lock__mutmut_53,
        "xǁAuditLockContextǁ_release_lock__mutmut_54": xǁAuditLockContextǁ_release_lock__mutmut_54,
    }

    def _release_lock(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAuditLockContextǁ_release_lock__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAuditLockContextǁ_release_lock__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _release_lock.__signature__ = _mutmut_signature(
        xǁAuditLockContextǁ_release_lock__mutmut_orig
    )
    xǁAuditLockContextǁ_release_lock__mutmut_orig.__name__ = (
        "xǁAuditLockContextǁ_release_lock"
    )

    async def release(self) -> None:
        """Manually release the lock."""
        await self._release_lock()


@asynccontextmanager
async def distributed_audit_lock(
    memory_id: str, timeout: int = 5
) -> AsyncIterator[None]:
    """
    Convenience context manager for distributed audit locking.

    Args:
        memory_id: The memory ID to lock.
        timeout: Lock timeout in seconds.

    Usage:
        async with distributed_audit_lock(memory_id, timeout=5):
            # Critical section - memory processing
            pass
    """
    lock = DistributedAuditLock()
    async with await lock.acquire(memory_id, timeout):
        yield


# Global instance for easy access
audit_lock = DistributedAuditLock()
