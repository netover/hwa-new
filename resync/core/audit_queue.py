"""
Redis-based Audit Queue for Resync

This module implements a scalable audit queue using Redis to replace SQLite.
The audit queue manages memories that need to be reviewed by administrators.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

import redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import RedisError

from resync.core.audit_lock import DistributedAuditLock
from resync.core.exceptions import (
    AuditError,
    DatabaseError,
    DataParsingError,
    FileProcessingError,
)
from resync.settings import settings

logger = logging.getLogger(__name__)


class IAuditQueue(ABC):
    """
    Abstract interface for audit queue implementations.
    """

    @abstractmethod
    async def add_audit_record(self, memory: Dict[str, Any]) -> bool:
        """Add a new memory to the audit queue."""

    @abstractmethod
    async def get_pending_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending audit records."""

    @abstractmethod
    async def update_audit_status(self, memory_id: str, status: str) -> bool:
        """Update the status of an audit record."""

    @abstractmethod
    async def is_memory_approved(self, memory_id: str) -> bool:
        """Check if a memory has been approved."""

    @abstractmethod
    async def delete_audit_record(self, memory_id: str) -> bool:
        """Remove an audit record from the queue."""

    @abstractmethod
    async def get_queue_length(self) -> int:
        """Get the current length of the audit queue."""

    @abstractmethod
    async def cleanup_processed_audits(self, days_old: int = 30) -> int:
        """Remove old processed audits."""


class AsyncAuditQueue(IAuditQueue):
    """
    Redis-based audit queue for managing memories that need admin review.

    Uses Redis for high-performance, scalable operations with atomic operations
    and pub/sub capabilities for real-time updates.
    """

    def __init__(self, redis_url: str = None, settings_module: Any = settings):
        """
        Initialize the Redis-based audit queue.

        Args:
            redis_url: Redis connection URL. Defaults to environment variable or settings.
            settings_module: The settings module to use (default: global settings).
        """
        self.settings = settings_module
        self.redis_url = redis_url or os.environ.get(
            "REDIS_URL",
            (
                self.settings.REDIS_URL
                if hasattr(self.settings, "REDIS_URL")
                else "redis://localhost:6379"
            ),
        )
        self.sync_client = redis.from_url(self.redis_url)
        self.async_client = AsyncRedis.from_url(self.redis_url)

        # Use the new distributed audit lock for consistency
        self.distributed_lock = DistributedAuditLock(self.redis_url)

        # Redis keys
        self.audit_queue_key = "resync:audit_queue"
        self.audit_status_key = "resync:audit_status"  # Hash for memory_id -> status
        self.audit_data_key = "resync:audit_data"  # Hash for memory_id -> JSON data

        logger.info(f"AsyncAuditQueue initialized with Redis at {self.redis_url}")

    async def add_audit_record(self, memory: Dict[str, Any]) -> bool:
        """
        Adds a new memory to the audit queue for review.

        Args:
            memory: Memory data to add to the queue.

        Returns:
            True if successfully added, False if already exists.
        """
        memory_id = memory["id"]

        # Check if already exists
        if await self.async_client.hexists(self.audit_status_key, memory_id):
            logger.warning(
                f"Memory {memory_id} already exists in audit queue. Skipping."
            )
            return False

        # Store memory data as JSON
        memory_data = {
            "memory_id": memory_id,
            "user_query": memory["user_query"],
            "agent_response": memory["agent_response"],
            "ia_audit_reason": memory.get("ia_audit_reason"),
            "ia_audit_confidence": memory.get("ia_audit_confidence"),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        async with self.async_client.pipeline() as pipe:
            # Add to queue (left push for FIFO)
            pipe.lpush(self.audit_queue_key, memory_id)
            # Store status
            pipe.hset(self.audit_status_key, memory_id, "pending")
            # Store data
            pipe.hset(self.audit_data_key, memory_id, json.dumps(memory_data))
            await pipe.execute()

        logger.info(f"Added memory {memory_id} to audit queue.")
        return True

    async def get_pending_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves pending audits from the queue.

        Args:
            limit: Maximum number of audits to return.

        Returns:
            List of pending audit records.
        """
        # Get memory IDs from queue
        memory_ids = await self.async_client.lrange(self.audit_queue_key, 0, limit - 1)

        if not memory_ids:
            return []

        # Get data for pending items only
        pending_audits = []
        for memory_id in memory_ids:
            memory_id_str = memory_id.decode("utf-8")
            status = await self.async_client.hget(self.audit_status_key, memory_id_str)

            if status and status.decode("utf-8") == "pending":
                data_json = await self.async_client.hget(
                    self.audit_data_key, memory_id_str
                )
                if data_json:
                    data = json.loads(data_json.decode("utf-8"))
                    pending_audits.append(data)

        return pending_audits

    async def update_audit_status(self, memory_id: str, status: str) -> bool:
        """
        Updates the status of an audit record.

        Args:
            memory_id: The memory ID to update.
            status: New status ('approved', 'rejected').

        Returns:
            True if successfully updated, False if not found.
        """
        # Check if exists
        current_status = await self.async_client.hget(self.audit_status_key, memory_id)
        if not current_status:
            logger.warning(f"Memory {memory_id} not found in audit queue.")
            return False

        # Update status
        async with self.async_client.pipeline() as pipe:
            pipe.hset(self.audit_status_key, memory_id, status)
            # Add reviewed timestamp to data
            data_json = await self.async_client.hget(self.audit_data_key, memory_id)
            if data_json:
                data = json.loads(data_json.decode("utf-8"))
                data["status"] = status
                data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
                pipe.hset(self.audit_data_key, memory_id, json.dumps(data))
            await pipe.execute()

        logger.info(f"Updated memory {memory_id} status to {status}.")
        return True

    async def is_memory_approved(self, memory_id: str) -> bool:
        """
        Checks if a memory has been approved by an admin.

        Args:
            memory_id: The memory ID to check.

        Returns:
            True if approved, False otherwise.
        """
        status = await self.async_client.hget(self.audit_status_key, memory_id)
        return status and status.decode("utf-8") == "approved"

    async def delete_audit_record(self, memory_id: str) -> bool:
        """
        Removes an audit record from the queue.

        Args:
            memory_id: The memory ID to remove.

        Returns:
            True if successfully removed, False if not found.
        """
        # Check if exists
        exists = await self.async_client.hexists(self.audit_status_key, memory_id)
        if not exists:
            logger.warning(f"Memory {memory_id} not found in audit queue.")
            return False

        async with self.async_client.pipeline() as pipe:
            # Remove from all Redis structures
            pipe.lrem(self.audit_queue_key, 0, memory_id)
            pipe.hdel(self.audit_status_key, memory_id)
            pipe.hdel(self.audit_data_key, memory_id)
            await pipe.execute()

        logger.info(f"Deleted memory {memory_id} from audit queue.")
        return True

    async def get_queue_length(self) -> int:
        """
        Gets the current length of the audit queue.

        Returns:
            Number of items in the queue.
        """
        return await self.async_client.llen(self.audit_queue_key)

    async def cleanup_processed_audits(self, days_old: int = 30) -> int:
        """
        Removes old processed (approved/rejected) audits to prevent memory bloat.

        Args:
            days_old: Remove audits older than this many days.

        Returns:
            Number of records cleaned up.
        """
        cutoff_date = datetime.now(timezone.utc).timestamp() - (days_old * 24 * 60 * 60)
        cleaned_count = 0

        # Get all memory IDs
        all_ids = await self.async_client.hkeys(self.audit_status_key)

        for memory_id_bytes in all_ids:
            memory_id = memory_id_bytes.decode("utf-8")
            status = await self.async_client.hget(self.audit_status_key, memory_id)

            if status and status.decode("utf-8") in ["approved", "rejected"]:
                # Check if old enough
                data_json = await self.async_client.hget(self.audit_data_key, memory_id)
                if data_json:
                    data = json.loads(data_json.decode("utf-8"))
                    reviewed_at_str = data.get("reviewed_at")
                    if reviewed_at_str:
                        reviewed_at = datetime.fromisoformat(
                            reviewed_at_str.replace("Z", "+00:00")
                        ).timestamp()
                        if reviewed_at < cutoff_date:
                            await self.delete_audit_record(memory_id)
                            cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old processed audits.")
        return cleaned_count

    # --- Distributed Locking for Race Condition Prevention ---

    async def acquire_lock(
        self, lock_key: str, lock_value: str, timeout: int = 30
    ) -> bool:
        """
        Acquires a distributed lock using the new DistributedAuditLock.

        Args:
            lock_key: Unique identifier for the lock
            lock_value: Unique value for this lock instance
            timeout: Lock timeout in seconds (default: 30)

        Returns:
            True if lock acquired, False if already locked
        """
        # Use the new distributed audit lock
        try:
            async with await self.distributed_lock.acquire(lock_key, timeout):
                return True
        except AuditError as e:
            logger.warning("Failed to acquire lock %s: %s", lock_key, e)
            return False
        except RedisError as e:
            logger.error("Redis error during lock acquisition for %s: %s", lock_key, e)
            return False

    async def release_lock(self, lock_key: str, lock_value: str) -> bool:
        """
        Releases a distributed lock using the new DistributedAuditLock.

        Args:
            lock_key: The lock key to release
            lock_value: The lock value (must match current owner)

        Returns:
            True if lock released, False if not owned or doesn't exist
        """
        # Use the new distributed audit lock for release
        try:
            await self.distributed_lock.force_release(lock_key)
            return True
        except AuditError as e:
            logger.warning("Failed to release lock %s: %s", lock_key, e)
            return False
        except RedisError as e:
            logger.error("Redis error during lock release for %s: %s", lock_key, e)
            return False
        except ValueError as e:
            logger.warning("Value error during lock release for %s: %s", lock_key, e)
            return False

    async def with_lock(self, lock_key: str, timeout: int = 30):
        """
        Context manager for distributed locking using the new DistributedAuditLock.

        Usage:
            async with audit_queue.with_lock(f"memory:{memory_id}"):
                # Critical section - memory processing
                pass
        """
        # Delegate to the new distributed audit lock
        return self.distributed_lock.acquire(lock_key, timeout)

    async def cleanup_expired_locks(
        self, lock_prefix: str = "memory:", max_age: int = 60
    ):
        """
        Cleans up expired locks to prevent deadlocks using the new DistributedAuditLock.

        Args:
            lock_prefix: Prefix for lock keys to clean up
            max_age: Maximum age in seconds for lock cleanup

        Returns:
            Number of locks cleaned up
        """
        # Delegate to the new distributed audit lock
        return await self.distributed_lock.cleanup_expired_locks(max_age)

    async def force_release_lock(self, lock_key: str) -> bool:
        """
        Forcefully releases a lock using the new DistributedAuditLock (for administrative purposes).

        Args:
            lock_key: The lock key to force release

        Returns:
            True if lock was released, False if not found
        """
        try:
            return await self.distributed_lock.force_release(lock_key)
        except AuditError as e:
            logger.error("Audit error force releasing lock %s: %s", lock_key, e)
            return False
        except RedisError as e:
            logger.error("Redis error force releasing lock %s: %s", lock_key, e)
            return False
        except ValueError as e:
            logger.error("Value error force releasing lock %s: %s", lock_key, e)
            return False
        except (ConnectionError, TimeoutError) as e:
            logger.error("Connection error force releasing lock %s: %s", lock_key, e)
            return False
        except Exception as e:
            logger.error("Unexpected error force releasing lock %s: %s", lock_key, e)
            return False

    async def get_all_audits(self) -> List[Dict[str, Any]]:
        """
        Retrieves all audit records from the queue.

        Returns:
            List of all audit records.
        """
        # Get all memory IDs
        memory_ids = await self.async_client.hkeys(self.audit_status_key)

        if not memory_ids:
            return []

        all_audits = []
        for memory_id_bytes in memory_ids:
            memory_id = memory_id_bytes.decode("utf-8")
            data_json = await self.async_client.hget(self.audit_data_key, memory_id)
            if data_json:
                data = json.loads(data_json.decode("utf-8"))
                all_audits.append(data)

        return all_audits

    async def get_audits_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Retrieves audit records filtered by status.

        Args:
            status: Status to filter by ('pending', 'approved', 'rejected')

        Returns:
            List of audit records with the specified status.
        """
        # Get all memory IDs
        memory_ids = await self.async_client.hkeys(self.audit_status_key)

        if not memory_ids:
            return []

        filtered_audits = []
        for memory_id_bytes in memory_ids:
            memory_id = memory_id_bytes.decode("utf-8")
            current_status = await self.async_client.hget(
                self.audit_status_key, memory_id
            )

            if current_status and current_status.decode("utf-8") == status:
                data_json = await self.async_client.hget(self.audit_data_key, memory_id)
                if data_json:
                    data = json.loads(data_json.decode("utf-8"))
                    filtered_audits.append(data)

        return filtered_audits

    async def get_audit_metrics(self) -> Dict[str, int]:
        """
        Returns metrics for the audit queue.

        Returns:
            Dictionary with counts of pending, approved, rejected, and total records.
        """
        # Get all memory IDs
        memory_ids = await self.async_client.hkeys(self.audit_status_key)

        if not memory_ids:
            return {"total": 0, "pending": 0, "approved": 0, "rejected": 0}

        metrics = {
            "total": len(memory_ids),
            "pending": 0,
            "approved": 0,
            "rejected": 0,
        }

        for memory_id_bytes in memory_ids:
            memory_id = memory_id_bytes.decode("utf-8")
            status = await self.async_client.hget(self.audit_status_key, memory_id)

            if status:
                status_str = status.decode("utf-8")
                if status_str in metrics:
                    metrics[status_str] += 1

        return metrics

    async def health_check(self) -> bool:
        """
        Performs a health check on the Redis connection.

        Returns:
            True if Redis is accessible, False otherwise.
        """
        try:
            # Simple ping to check if Redis is responsive
            return await self.async_client.ping()
        except RedisError as e:
            logger.error("Redis health check failed due to Redis error: %s", e)
            return False
        except ConnectionError as e:
            logger.error("Redis health check failed due to connection error: %s", e)
            return False
        except TimeoutError as e:
            logger.error("Redis health check failed due to timeout: %s", e)
            return False
        except Exception as e:
            logger.error("Redis health check failed due to unexpected error: %s", e)
            return False

    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Gets information about the Redis connection.

        Returns:
            Dictionary with connection information.
        """
        try:
            info = await self.async_client.info()
            return {
                "connected": True,
                "host": self.redis_url,
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "uptime_days": info.get("uptime_in_days", 0),
            }
        except RedisError as e:
            logger.error("Redis error getting connection info: %s", e)
            return {
                "connected": False,
                "host": self.redis_url,
                "error": f"Redis error: {str(e)}",
            }
        except ConnectionError as e:
            logger.error("Connection error getting Redis info: %s", e)
            return {
                "connected": False,
                "host": self.redis_url,
                "error": f"Connection error: {str(e)}",
            }
        except TimeoutError as e:
            logger.error("Timeout getting Redis connection info: %s", e)
            return {
                "connected": False,
                "host": self.redis_url,
                "error": f"Timeout: {str(e)}",
            }
        except Exception as e:
            logger.error("Unexpected error getting Redis connection info: %s", e)
            return {
                "connected": False,
                "host": self.redis_url,
                "error": f"Unexpected error: {str(e)}",
            }

    def health_check_sync(self) -> bool:
        """Synchronous wrapper for health_check"""
        import asyncio

        return asyncio.run(self.health_check())

    def get_connection_info_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_connection_info"""
        import asyncio

        return asyncio.run(self.get_connection_info())

    # Synchronous wrappers for FastAPI compatibility
    def get_all_audits_sync(self) -> List[Dict[str, Any]]:
        """Synchronous wrapper for get_all_audits"""
        import asyncio

        return asyncio.run(self.get_all_audits())

    def get_audits_by_status_sync(self, status: str) -> List[Dict[str, Any]]:
        """Synchronous wrapper for get_audits_by_status"""
        import asyncio

        return asyncio.run(self.get_audits_by_status(status))

    def get_audit_metrics_sync(self) -> Dict[str, int]:
        """Synchronous wrapper for get_audit_metrics"""
        import asyncio

        return asyncio.run(self.get_audit_metrics())

    def update_audit_status_sync(self, memory_id: str, status: str) -> bool:
        """Synchronous wrapper for update_audit_status"""
        import asyncio

        return asyncio.run(self.update_audit_status(memory_id, status))

    def delete_audit_record_sync(self, memory_id: str) -> bool:
        """Synchronous wrapper for delete_audit_record"""
        import asyncio

        return asyncio.run(self.delete_audit_record(memory_id))

    def is_memory_approved_sync(self, memory_id: str) -> bool:
        """Synchronous wrapper for is_memory_approved"""
        import asyncio

        return asyncio.run(self.is_memory_approved(memory_id))


# Factory function for creating AsyncAuditQueue instances
def create_audit_queue(
    redis_url: str = None, settings_module: Any = settings
) -> AsyncAuditQueue:
    """Create and return a new AsyncAuditQueue instance."""
    return AsyncAuditQueue(redis_url=redis_url, settings_module=settings_module)


# Legacy compatibility: create a default instance
# This will be removed once all code is migrated to DI
import warnings

warnings.warn(
    "The global audit_queue instance is deprecated and will be removed in a future version. "
    "Use dependency injection with IAuditQueue instead.",
    DeprecationWarning,
    stacklevel=2,
)
audit_queue = create_audit_queue()


# Migration utilities for transitioning from SQLite
async def migrate_from_sqlite():
    """
    Migrates existing audit data from SQLite to Redis.
    This should be run once during deployment.
    """
    try:
        import sqlite3

        sqlite_path = settings.BASE_DIR / "audit_queue.db"
        if not sqlite_path.exists():
            logger.info("No SQLite audit database found, skipping migration.")
            return

        # Connect to SQLite
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all records
        cursor.execute("SELECT * FROM audit_queue")
        rows = cursor.fetchall()

        migrated_count = 0
        for row in rows:
            memory = {
                "id": row["memory_id"],
                "user_query": row["user_query"],
                "agent_response": row["agent_response"],
                "ia_audit_reason": row["ia_audit_reason"],
                "ia_audit_confidence": row["ia_audit_confidence"],
            }

            success = await audit_queue.add_audit_record(memory)
            if success:
                migrated_count += 1

                # Update status if not pending
                if row["status"] != "pending":
                    await audit_queue.update_audit_status(
                        row["memory_id"], row["status"]
                    )

        logger.info(
            f"Migration completed: {migrated_count} records migrated from SQLite to Redis."
        )
        conn.close()

    except ImportError as e:
        logger.error(
            "Import error during SQLite to Redis migration: %s", e, exc_info=True
        )
        raise FileProcessingError(
            f"Import error during SQLite to Redis migration: {e}"
        ) from e
    except sqlite3.Error as e:
        logger.error("SQLite error during migration: %s", e, exc_info=True)
        raise DatabaseError(f"SQLite error during migration: {e}") from e
    except RedisError as e:
        logger.error("Redis error during migration: %s", e, exc_info=True)
        raise DatabaseError(f"Redis error during migration: {e}") from e
    except json.JSONDecodeError as e:
        logger.error("JSON decode error during migration: %s", e, exc_info=True)
        raise DataParsingError(f"JSON decode error during migration: {e}") from e
    except FileNotFoundError as e:
        logger.error("File not found during migration: %s", e, exc_info=True)
        raise FileProcessingError(f"File not found during migration: {e}") from e
    except Exception as e:
        logger.error(
            "Unexpected error during SQLite to Redis migration: %s", e, exc_info=True
        )
        raise AuditError(
            f"Unexpected error during SQLite to Redis migration: {e}"
        ) from e
