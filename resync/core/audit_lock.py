"""
Distributed Audit Lock for Resync

This module provides a dedicated distributed locking mechanism for audit operations
to prevent race conditions during concurrent memory processing.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from redis.asyncio import Redis as AsyncRedis

from resync.settings import settings

logger = logging.getLogger(__name__)


class DistributedAuditLock:
    """
    A distributed lock implementation using Redis for audit operations.

    This class provides atomic locking to prevent race conditions when multiple
    IA Auditor processes attempt to process the same memory simultaneously.
    """

    def __init__(self, redis_url: str = None):
        """
        Initialize the distributed audit lock.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or localhost.
        """
        self.redis_url = redis_url or getattr(
            settings, "REDIS_URL", "redis://localhost:6379"
        )
        self.client: Optional[AsyncRedis] = None
        self._lock_prefix = "audit_lock"

        logger.info(f"DistributedAuditLock initialized with Redis at {self.redis_url}")

    async def connect(self):
        """Initialize Redis connection."""
        if self.client is None:
self.client = AsyncRedis.from_url(self.redis_url)
# Load Lua script on connection
self.release_script_sha = await self.client.script_load(lua_script)
# Test connection
await self.client.ping()
logger.info("DistributedAuditLock connected to Redis")
# Load Lua script on connection
if hasattr(self.client, 'script'):
    self.release_script_sha = await self.client.script().load(lua_script)
else:
    self.release_script_sha = None
            self.client = AsyncRedis.from_url(self.redis_url)
            # Test connection
            await self.client.ping()
            logger.info("DistributedAuditLock connected to Redis")

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("DistributedAuditLock disconnected from Redis")

    def _get_lock_key(self, memory_id: str) -> str:
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

    async def acquire(self, memory_id: str, timeout: int = 5) -> "AuditLockContext":
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

        lock_key = self._get_lock_key(memory_id)
        return AuditLockContext(self.client, lock_key, timeout)

    async def is_locked(self, memory_id: str) -> bool:
        """
        Check if a memory ID is currently locked.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if locked, False otherwise.
        """
        if self.client is None:
            await self.connect()

        lock_key = self._get_lock_key(memory_id)
        return await self.client.exists(lock_key) == 1

    async def force_release(self, memory_id: str) -> bool:
        """
        Forcefully release a lock for a memory ID (for administrative purposes).

        Args:
            memory_id: The memory ID to unlock.

        Returns:
            True if lock was released, False if not found.
        """
        if self.client is None:
            await self.connect()

        lock_key = self._get_lock_key(memory_id)
        result = await self.client.delete(lock_key)
        if result:
            logger.warning(f"Forcefully released audit lock for memory: {memory_id}")
        return bool(result)

    async def cleanup_expired_locks(self, max_age: int = 60) -> int:
        """
        Clean up expired locks to prevent deadlocks.

        Args:
            max_age: Maximum age in seconds for lock cleanup.

        Returns:
            Number of locks cleaned up.
        """
        if self.client is None:
            await self.connect()

        try:
            cleaned_count = 0

            # Get all audit lock keys
            lock_pattern = f"{self._lock_prefix}:*"
            lock_keys = await self.client.keys(lock_pattern)

            for lock_key_bytes in lock_keys:
                lock_key = lock_key_bytes.decode("utf-8")

                # Check if lock is old enough to be considered expired
                ttl = await self.client.ttl(lock_key)
                if ttl == -1:  # No TTL set
                    # Force expire locks older than max_age
                    await self.client.expire(lock_key, max_age)
                elif ttl > max_age:
                    # Remove locks that are too old
                    await self.client.delete(lock_key)
                    cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired audit locks")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired audit locks: {e}")
            return 0


class AuditLockContext:
    """
    Context manager for distributed audit locks.

    Usage:
        async with audit_lock.acquire(memory_id, timeout=5):
            # Critical section - memory processing
            pass
    """

    def __init__(self, client: AsyncRedis, lock_key: str, timeout: int):
        """
        Initialize the lock context.

        Args:
            client: Redis async client.
            lock_key: The lock key to acquire.
            timeout: Lock timeout in seconds.
        """
        self.client = client
        self.lock_key = lock_key
        self.timeout = timeout
        self.lock_value = None
        self._locked = False

    async def __aenter__(self):
        """Acquire the lock."""
        self.lock_value = str(uuid.uuid4())

        # Use Redis SET with NX and PX for atomic lock acquisition
        success = await self.client.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # Only set if key doesn't exist
            px=self.timeout * 1000,  # Convert seconds to milliseconds
        )

async def _release_lock(self):
    """Release the lock if owned by this instance."""
    if not self.lock_value:
        return

    # Validate lock key and value
    if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
        raise ValueError("Invalid lock key format - must be non-empty string")

    if not isinstance(self.lock_value, str) or len(self.lock_value) != 36 or not self.lock_value.count('-') == 4:
        raise ValueError("Invalid lock value (must be a UUID)")

    try:
        # Use EVALSHA for atomic check-and-delete
        if self.release_script_sha:
            try:
                result = await self.client.evalsha(self.release_script_sha, 1, self.lock_key, self.lock_value)
            except redis.errors.ScriptError as e:
                logger.error(f"Script error executing release script: {e}")
                raise
            except redis.errors.RedisError as e:
                logger.error(f"Redis error during lock release: {e}")
                raise
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
            result = await self.client.eval(lua_script, 1, self.lock_key, self.lock_value)
        
        if result == 1:
            logger.debug(f"Released audit lock: {self.lock_key}")
        else:
            logger.warning(
                f"Failed to release audit lock: {self.lock_key} (may have expired)"
            )
    
    except Exception as e:
        logger.error(f"Error executing Redis script during lock release: {str(e)}")
        raise
        if success:
            self._locked = True
async def _release_lock(self):
# Validate lock key and value
if not self.lock_value:
    return

# Validate lock key format
if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
    raise ValueError("Invalid lock key format - must be non-empty string")

# Validate lock value is a UUID
if not isinstance(self.lock_value, str) or len(self.lock_value) != 36 or not self.lock_value.count('-') == 4:
    raise ValueError("Invalid lock value (must be a UUID)")
    """Release the lock if owned by this instance."""
    if not self.lock_value:
        return

    # Validate lock key and value
    if not isinstance(self.lock_key, str) or len(self.lock_key) == 0:
        raise ValueError("Invalid lock key format")
    if not isinstance(self.lock_value, str) or len(self.lock_value) != 36 or not self.lock_value.count('-') == 4:
        raise ValueError("Invalid lock value (must be a UUID)")
    
    try:
        # Use EVALSHA for atomic check-and-delete
        if self.release_script_sha:
            result = await self.client.evalsha(self.release_script_sha, 1, self.lock_key, self.lock_value)
        else:
            # Fallback to eval if script not loaded
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = await self.client.eval(lua_script, 1, self.lock_key, self.lock_value)
        
        if result == 1:
            logger.debug(f"Released audit lock: {self.lock_key}")
        else:
            logger.warning(
                f"Failed to release audit lock: {self.lock_key} (may have expired)"
            )
    
    except Exception as e:
        logger.error(f"Error executing Redis script during lock release: {str(e)}")
        raise
            logger.debug(f"Acquired audit lock: {self.lock_key}")
            return self
        else:
            raise Exception(f"Could not acquire audit lock: {self.lock_key}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release the lock."""
        if self._locked and self.lock_value:
            await self._release_lock()

    async def _release_lock(self):
        """Release the lock if owned by this instance."""
        if not self.lock_value:
            return

        # Use Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
result = await self.client.evalsha(self.release_script_sha, 1, self.lock_key, self.lock_value)
        """

lua_script = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""
# Load script on connection
self.release_script_sha = None
        result = await self.client.eval(lua_script, 1, self.lock_key, self.lock_value)
        if result == 1:
            logger.debug(f"Released audit lock: {self.lock_key}")
        else:
            logger.warning(
                f"Failed to release audit lock: {self.lock_key} (may have expired)"
            )

        self._locked = False
        self.lock_value = None

    async def release(self):
        """Manually release the lock."""
        await self._release_lock()


@asynccontextmanager
async def distributed_audit_lock(memory_id: str, timeout: int = 5):
    """
    Convenience context manager for distributed audit locking.

    Args:
        memory_id: The memory ID to lock.
        timeout: Lock timeout in seconds.

    Usage:
        async with distributed_audit_lock(memory_id, timeout=5):
            # Critical section
            pass
    """
    lock = DistributedAuditLock()
    async with await lock.acquire(memory_id, timeout):
        yield


# Global instance for easy access
audit_lock = DistributedAuditLock()
