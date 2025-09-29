from unittest.mock import MagicMock

import redis


class TestAsyncAuditQueue:
    """Test suite for AsyncAuditQueue functionality."""

    async def test_cleanup_expired_locks_transaction(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test transactional cleanup of expired locks with Redis MULTI/EXEC."""
        # Mock Redis methods for transaction simulation
        mock_pipeline = MagicMock()
        mock_pipeline.watch.return_value = None
        mock_pipeline.multi.return_value = mock_pipeline
        mock_pipeline.exec.return_value = [2]  # Number of deleted keys

        monkeypatch.setattr(audit_queue.redis_client, "pipeline", lambda: mock_pipeline)

        # Mock keys and ttl to simulate expired locks
        audit_queue.redis_client.keys.return_value = [
            b"memory:expired1",
            b"memory:expired2",
        ]
        audit_queue.redis_client.ttl.side_effect = [-1, -1]

        # Execute cleanup
        result = await audit_queue.cleanup_expired_locks()

        assert result == 2
        mock_pipeline.watch.assert_called_once_with(b"memory:*")
        mock_pipeline.multi.assert_called_once()
        mock_pipeline.exec.assert_called_once()

    async def test_cleanup_expired_locks_transaction_retry(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test transaction retry on WatchError during cleanup."""
        # Simulate WatchError and successful retry
        mock_pipeline = MagicMock()
        mock_pipeline.watch.side_effect = [
            redis.exceptions.WatchError("Another client modified the key"),
            None,
        ]
        mock_pipeline.multi.return_value = mock_pipeline
        mock_pipeline.exec.side_effect = [None, 2]  # First abort, second commit

        monkeypatch.setattr(audit_queue.redis_client, "pipeline", lambda: mock_pipeline)

        # Mock keys and ttl to simulate expired locks
        audit_queue.redis_client.keys.return_value = [
            b"memory:expired1",
            b"memory:expired2",
        ]
        audit_queue.redis_client.ttl.side_effect = [-1, -1]

        # Execute cleanup with retry
        result = await audit_queue.cleanup_expired_locks()

        assert result == 2
        assert mock_pipeline.watch.call_count == 2
        assert mock_pipeline.exec.call_count == 2

    async def test_cleanup_expired_locks_atomicity(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test atomicity of cleanup operations with partial failure simulation."""
        # Mock pipeline to simulate failure after partial execution
        mock_pipeline = MagicMock()
        mock_pipeline.watch.return_value = None
        mock_pipeline.multi.return_value = mock_pipeline
        # Simulate Redis returning None after executing some operations
        mock_pipeline.exec.return_value = None

        monkeypatch.setattr(audit_queue.redis_client, "pipeline", lambda: mock_pipeline)

        # Mock keys and ttl to simulate expired locks
        audit_queue.redis_client.keys.return_value = [
            b"memory:expired1",
            b"memory:expired2",
        ]
        audit_queue.redis_client.ttl.side_effect = [-1, -1]

        # Should not delete any keys due to atomic transaction failure
        result = await audit_queue.cleanup_expired_locks()

        assert result == 0
        mock_pipeline.delete.assert_any_call(b"memory:expired1")
        mock_pipeline.delete.assert_any_call(b"memory:expired2")
        # Verify no keys were actually deleted
        assert await audit_queue.mock_redis_client.exists(b"memory:expired1") == 1
        assert await audit_queue.mock_redis_client.exists(b"memory:expired2") == 1

    async def test_cleanup_expired_locks_exponential_backoff(
        self, audit_queue, mock_redis_client, monkeypatch
    ):
        """Test exponential backoff behavior during transaction conflicts."""
        # Simulate WatchError three times then success
        mock_pipeline = MagicMock()
        mock_pipeline.watch.side_effect = [
            redis.exceptions.WatchError("Conflict"),
            redis.exceptions.WatchError("Conflict"),
            None,
        ]
        mock_pipeline.multi.return_value = mock_pipeline
        mock_pipeline.exec.side_effect = [None, None, 2]

        monkeypatch.setattr(audit_queue.redis_client, "pipeline", lambda: mock_pipeline)

        # Mock keys and ttl to simulate expired locks
        audit_queue.redis_client.keys.return_value = [
            b"memory:expired1",
            b"memory:expired2",
        ]
        audit_queue.redis_client.ttl.side_effect = [-1, -1]

        # Execute cleanup with retry
        result = await audit_queue.cleanup_expired_locks()

        assert result == 2
        assert mock_pipeline.watch.call_count == 3
        assert mock_pipeline.exec.call_count == 3

    async def test_cleanup_expired_locks_no_expired_keys(
        self, audit_queue, mock_redis_client
    ):
        """Test cleanup when no expired locks exist."""
        mock_redis_client.keys.return_value = []

        result = await audit_queue.cleanup_expired_locks()
        assert result == 0

    async def test_cleanup_expired_locks_all_keys_valid(
        self, audit_queue, mock_redis_client
    ):
        """Test cleanup when all keys are still valid."""
        mock_redis_client.keys.return_value = [b"memory:valid1", b"memory:valid2"]
        mock_redis_client.ttl.return_value = 3600  # 1 hour TTL

        result = await audit_queue.cleanup_expired_locks()
        assert result == 0
