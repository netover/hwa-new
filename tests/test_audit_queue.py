import pytest
from unittest.mock import AsyncMock, MagicMock

import redis


class TestAsyncAuditQueue:
    """Test suite for AsyncAuditQueue functionality."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_delegation(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test that cleanup_expired_locks delegates to distributed_lock."""
        # Mock the distributed_lock.cleanup_expired_locks method
        audit_queue.distributed_lock.cleanup_expired_locks = AsyncMock(return_value=5)

        # Execute cleanup
        result = await audit_queue.cleanup_expired_locks(max_age=120)

        assert result == 5
        audit_queue.distributed_lock.cleanup_expired_locks.assert_called_once_with(120)

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_error_handling(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test error handling in cleanup_expired_locks."""
        # Mock the distributed_lock to raise an exception
        audit_queue.distributed_lock.cleanup_expired_locks = AsyncMock(
            side_effect=Exception("Redis connection failed")
        )

        # Execute cleanup - should handle the error gracefully
        result = await audit_queue.cleanup_expired_locks()

        assert result == 0  # Should return 0 on error
        audit_queue.distributed_lock.cleanup_expired_locks.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_default_behavior(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test cleanup_expired_locks default behavior."""
        # Mock the distributed_lock to return 0 (no locks cleaned)
        audit_queue.distributed_lock.cleanup_expired_locks = AsyncMock(return_value=0)

        # Execute cleanup
        result = await audit_queue.cleanup_expired_locks()

        assert result == 0
        audit_queue.distributed_lock.cleanup_expired_locks.assert_called_once_with(60)  # default max_age

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_with_custom_age(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test cleanup_expired_locks with custom max_age parameter."""
        # Mock the distributed_lock to return 3 (3 locks cleaned)
        audit_queue.distributed_lock.cleanup_expired_locks = AsyncMock(return_value=3)

        # Execute cleanup with custom age
        result = await audit_queue.cleanup_expired_locks(max_age=3600)  # 1 hour

        assert result == 3
        audit_queue.distributed_lock.cleanup_expired_locks.assert_called_once_with(3600)

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_no_expired_keys(
        self, audit_queue, mock_redis_client
    ):
        """Test cleanup when no expired locks exist."""
        mock_redis_client.keys.return_value = []

        result = await audit_queue.cleanup_expired_locks()
        assert result == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_locks_all_keys_valid(
        self, audit_queue, mock_redis_client
    ):
        """Test cleanup when all keys are still valid."""
        mock_redis_client.keys.return_value = [b"memory:valid1", b"memory:valid2"]
        mock_redis_client.ttl.return_value = 3600  # 1 hour TTL

        result = await audit_queue.cleanup_expired_locks()
        assert result == 0
