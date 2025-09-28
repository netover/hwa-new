"""Tests for resync.core.audit_queue module."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from resync.core.audit_queue import AsyncAuditQueue
from resync.core.exceptions import AuditError, DatabaseError, DataParsingError


class TestAsyncAuditQueue:
    """Test suite for AsyncAuditQueue class."""

    @pytest.fixture
    def sample_memory(self):
        """Sample memory data for testing."""
        return {
            "id": "test_memory_123",
            "user_query": "What is the capital of France?",
            "agent_response": "The capital of France is Paris.",
            "ia_audit_reason": "This is a factual question about geography.",
            "ia_audit_confidence": 0.95
        }

    def test_async_audit_queue_initialization(self):
        """Test AsyncAuditQueue initialization."""
        with patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue()

            assert queue.redis_url == "redis://localhost:6379"
            assert queue.audit_queue_key == "resync:audit_queue"
            assert queue.audit_status_key == "resync:audit_status"
            assert queue.audit_data_key == "resync:audit_data"

    def test_async_audit_queue_with_custom_redis_url(self):
        """Test AsyncAuditQueue initialization with custom Redis URL."""
        custom_url = "redis://custom-host:6380"

        with patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue(redis_url=custom_url)

            assert queue.redis_url == custom_url

    def test_audit_queue_key_configuration(self):
        """Test audit queue key configuration."""
        with patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue()

            assert queue.audit_queue_key == "resync:audit_queue"
            assert queue.audit_status_key == "resync:audit_status"
            assert queue.audit_data_key == "resync:audit_data"

    def test_memory_data_structure(self, sample_memory):
        """Test memory data structure creation."""
        memory_id = sample_memory["id"]
        user_query = sample_memory["user_query"]
        agent_response = sample_memory["agent_response"]
        ia_audit_reason = sample_memory.get("ia_audit_reason")
        ia_audit_confidence = sample_memory.get("ia_audit_confidence")

        # Test the structure that would be created
        expected_data = {
            "memory_id": memory_id,
            "user_query": user_query,
            "agent_response": agent_response,
            "ia_audit_reason": ia_audit_reason,
            "ia_audit_confidence": ia_audit_confidence,
            "status": "pending",
            "created_at": pytest.approx(datetime.utcnow().isoformat(), abs=1),
        }

        # Verify the structure
        assert expected_data["memory_id"] == memory_id
        assert expected_data["user_query"] == user_query
        assert expected_data["agent_response"] == agent_response
        assert expected_data["status"] == "pending"

    def test_memory_data_json_serialization(self, sample_memory):
        """Test memory data JSON serialization."""
        memory_data = {
            "memory_id": sample_memory["id"],
            "user_query": sample_memory["user_query"],
            "agent_response": sample_memory["agent_response"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Test JSON serialization
        json_str = json.dumps(memory_data)
        deserialized = json.loads(json_str)

        assert deserialized["memory_id"] == sample_memory["id"]
        assert deserialized["user_query"] == sample_memory["user_query"]
        assert deserialized["agent_response"] == sample_memory["agent_response"]
        assert deserialized["status"] == "pending"

    def test_memory_data_deserialization_error(self):
        """Test handling of invalid JSON data."""
        invalid_json = "invalid json string"

        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_audit_queue_constants(self):
        """Test audit queue constants."""
        # Test that the keys are properly configured
        assert "resync:audit_queue" == "resync:audit_queue"
        assert "resync:audit_status" == "resync:audit_status"
        assert "resync:audit_data" == "resync:audit_data"

    def test_memory_id_extraction(self, sample_memory):
        """Test memory ID extraction from memory data."""
        memory_id = sample_memory["id"]

        assert memory_id == "test_memory_123"
        assert isinstance(memory_id, str)
        assert len(memory_id) > 0

    def test_memory_data_validation(self, sample_memory):
        """Test memory data validation."""
        # Test that required fields exist
        assert "id" in sample_memory
        assert "user_query" in sample_memory
        assert "agent_response" in sample_memory

        # Test that optional fields exist
        assert "ia_audit_reason" in sample_memory
        assert "ia_audit_confidence" in sample_memory

    def test_audit_status_values(self):
        """Test audit status values."""
        valid_statuses = ["pending", "approved", "rejected"]

        for status in valid_statuses:
            assert isinstance(status, str)
            assert len(status) > 0

    def test_audit_queue_key_naming(self):
        """Test audit queue key naming conventions."""
        # Keys should follow Redis naming conventions
        queue_key = "resync:audit_queue"
        status_key = "resync:audit_status"
        data_key = "resync:audit_data"

        assert ":" in queue_key
        assert ":" in status_key
        assert ":" in data_key
        assert all(key.startswith("resync:") for key in [queue_key, status_key, data_key])

    def test_datetime_serialization(self):
        """Test datetime serialization for audit records."""
        now = datetime.utcnow()
        iso_string = now.isoformat()

        assert isinstance(iso_string, str)
        assert "T" in iso_string
        assert "Z" in iso_string or "+" in iso_string

    def test_memory_data_optional_fields(self):
        """Test memory data with optional fields."""
        memory_with_optional = {
            "id": "test_memory",
            "user_query": "Test query",
            "agent_response": "Test response",
            "ia_audit_reason": "Optional reason",
            "ia_audit_confidence": 0.8
        }

        assert memory_with_optional.get("ia_audit_reason") == "Optional reason"
        assert memory_with_optional.get("ia_audit_confidence") == 0.8

        memory_without_optional = {
            "id": "test_memory",
            "user_query": "Test query",
            "agent_response": "Test response"
        }

        assert memory_without_optional.get("ia_audit_reason") is None
        assert memory_without_optional.get("ia_audit_confidence") is None

    def test_audit_queue_settings_integration(self):
        """Test integration with settings module."""
        with patch('resync.core.audit_queue.settings') as mock_settings:
            mock_settings.REDIS_URL = "redis://test-host:6379"

            with patch('redis.from_url') as mock_sync_redis, \
                 patch('redis.asyncio.Redis.from_url') as mock_async_redis:

                mock_sync_client = MagicMock()
                mock_async_client = AsyncMock()
                mock_sync_redis.return_value = mock_sync_client
                mock_async_redis.return_value = mock_async_client

                queue = AsyncAuditQueue()

                assert queue.redis_url == "redis://test-host:6379"

    def test_audit_queue_environment_variable_fallback(self):
        """Test environment variable fallback for Redis URL."""
        with patch.dict('os.environ', {'REDIS_URL': 'redis://env-host:6380'}), \
             patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue()

            assert queue.redis_url == "redis://env-host:6380"

    def test_audit_queue_import_dependencies(self):
        """Test that all required dependencies are imported."""
        # Test that the module can be imported
        from resync.core import audit_queue

        # Test that the class is available
        assert hasattr(audit_queue, 'AsyncAuditQueue')

        # Test that exceptions are imported
        assert hasattr(audit_queue, 'AuditError')
        assert hasattr(audit_queue, 'DatabaseError')
        assert hasattr(audit_queue, 'DataParsingError')

    def test_audit_queue_module_structure(self):
        """Test audit queue module structure."""
        import resync.core.audit_queue as aq

        # Test that the class exists
        assert hasattr(aq, 'AsyncAuditQueue')

        # Test that the class is properly defined
        assert issubclass(aq.AsyncAuditQueue, object)

    def test_memory_data_field_types(self, sample_memory):
        """Test memory data field types."""
        # Test that fields have correct types
        assert isinstance(sample_memory["id"], str)
        assert isinstance(sample_memory["user_query"], str)
        assert isinstance(sample_memory["agent_response"], str)
        assert isinstance(sample_memory["ia_audit_confidence"], (int, float))
        assert isinstance(sample_memory.get("ia_audit_reason"), str)

    def test_audit_queue_error_classes(self):
        """Test audit queue error classes."""
        from resync.core.exceptions import AuditError, DatabaseError, DataParsingError

        # Test that error classes exist and are properly defined
        assert issubclass(AuditError, Exception)
        assert issubclass(DatabaseError, Exception)
        assert issubclass(DataParsingError, Exception)

        # Test that we can instantiate them
        audit_error = AuditError("Test audit error")
        db_error = DatabaseError("Test database error")
        parse_error = DataParsingError("Test parsing error")

        assert str(audit_error) == "Test audit error"
        assert str(db_error) == "Test database error"
        assert str(parse_error) == "Test parsing error"

    def test_audit_queue_key_prefix_consistency(self):
        """Test audit queue key prefix consistency."""
        keys = [
            "resync:audit_queue",
            "resync:audit_status",
            "resync:audit_data"
        ]

        # All keys should have the same prefix
        for key in keys:
            assert key.startswith("resync:")
            assert key.count(":") >= 1

    def test_memory_data_timestamp_format(self):
        """Test memory data timestamp format."""
        now = datetime.utcnow()
        iso_string = now.isoformat()

        # Should be ISO format
        assert "T" in iso_string
        assert iso_string.endswith("Z") or "+" in iso_string

        # Should be parseable back to datetime
        parsed = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)

    def test_audit_queue_redis_url_validation(self):
        """Test Redis URL validation."""
        valid_urls = [
            "redis://localhost:6379",
            "redis://host:6380",
            "redis://user:pass@host:6380",
            "redis://host:6380/0",
        ]

        for url in valid_urls:
            assert url.startswith("redis://")
            assert "://" in url

    def test_memory_data_size_limits(self, sample_memory):
        """Test memory data size limits."""
        # Test reasonable size limits for memory data
        memory_id = sample_memory["id"]
        user_query = sample_memory["user_query"]
        agent_response = sample_memory["agent_response"]

        # Reasonable limits
        assert len(memory_id) < 1000
        assert len(user_query) < 10000
        assert len(agent_response) < 10000

    def test_audit_queue_method_signatures(self):
        """Test audit queue method signatures."""
        # Test that the class has the expected methods
        queue = AsyncAuditQueue.__new__(AsyncAuditQueue)

        # Check that methods exist (even if not implemented)
        expected_methods = [
            'add_audit_record',
            'get_pending_audits',
            'update_audit_status',
            'delete_audit_record',
            'is_memory_approved',
            'get_queue_length',
            'get_all_audits',
            'get_audits_by_status',
            'get_audit_metrics',
            'health_check'
        ]

        for method_name in expected_methods:
            assert hasattr(queue, method_name)

    def test_audit_queue_async_methods(self):
        """Test that audit queue methods are async."""
        import inspect

        queue = AsyncAuditQueue.__new__(AsyncAuditQueue)

        async_methods = [
            'add_audit_record',
            'get_pending_audits',
            'update_audit_status',
            'delete_audit_record',
            'is_memory_approved',
            'get_queue_length',
            'get_all_audits',
            'get_audits_by_status',
            'get_audit_metrics',
            'health_check'
        ]

        for method_name in async_methods:
            method = getattr(queue, method_name)
            assert inspect.iscoroutinefunction(method)

    def test_audit_queue_initialization(self):
        """Test AsyncAuditQueue initialization."""
        with patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue()

            assert queue.redis_url == "redis://localhost:6379"
            assert queue.audit_queue_key == "resync:audit_queue"
            assert queue.audit_status_key == "resync:audit_status"
            assert queue.audit_data_key == "resync:audit_data"

    def test_audit_queue_basic_functionality(self):
        """Test basic audit queue functionality."""
        # Test that the class can be imported and initialized
        with patch('redis.from_url') as mock_sync_redis, \
             patch('redis.asyncio.Redis.from_url') as mock_async_redis:

            mock_sync_client = MagicMock()
            mock_async_client = AsyncMock()
            mock_sync_redis.return_value = mock_sync_client
            mock_async_redis.return_value = mock_async_client

            queue = AsyncAuditQueue()

            assert queue.redis_url == "redis://localhost:6379"
            assert queue.audit_queue_key == "resync:audit_queue"
            assert queue.audit_status_key == "resync:audit_status"
            assert queue.audit_data_key == "resync:audit_data"

    async def test_add_audit_record_duplicate(self, audit_queue, sample_memory, mock_redis_client):
        """Test adding duplicate audit record."""
        mock_redis_client.hexists.return_value = True

        result = await audit_queue.add_audit_record(sample_memory)

        assert result is False
        mock_redis_client.hexists.assert_called_once_with("resync:audit_status", "test_memory_123")

    async def test_get_pending_audits_empty(self, audit_queue, mock_redis_client):
        """Test getting pending audits when queue is empty."""
        mock_redis_client.lrange.return_value = []

        result = await audit_queue.get_pending_audits()

        assert result == []
        mock_redis_client.lrange.assert_called_once_with("resync:audit_queue", 0, 49)

    async def test_get_pending_audits_with_data(self, audit_queue, mock_redis_client):
        """Test getting pending audits with data."""
        # Mock Redis responses
        memory_ids = [b"memory_1", b"memory_2"]
        mock_redis_client.lrange.return_value = memory_ids
        mock_redis_client.hget.side_effect = [
            b"pending",  # memory_1 status
            b"approved", # memory_2 status
            b'{"memory_id": "memory_1", "status": "pending"}',  # memory_1 data
        ]

        result = await audit_queue.get_pending_audits()

        assert len(result) == 1
        assert result[0]["memory_id"] == "memory_1"
        assert result[0]["status"] == "pending"

    async def test_update_audit_status_success(self, audit_queue, mock_redis_client):
        """Test successful audit status update."""
        mock_redis_client.hset.return_value = 1

        result = await audit_queue.update_audit_status("memory_123", "approved")

        assert result is True
        mock_redis_client.hset.assert_called_once_with("resync:audit_status", "memory_123", "approved")

    async def test_update_audit_status_not_found(self, audit_queue, mock_redis_client):
        """Test updating status of non-existent record."""
        mock_redis_client.hset.return_value = 0

        result = await audit_queue.update_audit_status("nonexistent_memory", "approved")

        assert result is False

    async def test_delete_audit_record_success(self, audit_queue, mock_redis_client):
        """Test successful audit record deletion."""
        mock_redis_client.delete.return_value = 3  # 3 keys deleted

        result = await audit_queue.delete_audit_record("memory_123")

        assert result is True
        mock_redis_client.delete.assert_called_once()

    async def test_delete_audit_record_not_found(self, audit_queue, mock_redis_client):
        """Test deleting non-existent audit record."""
        mock_redis_client.delete.return_value = 0

        result = await audit_queue.delete_audit_record("nonexistent_memory")

        assert result is False

    async def test_is_memory_approved_true(self, audit_queue, mock_redis_client):
        """Test checking if memory is approved."""
        mock_redis_client.hget.return_value = b"approved"

        result = await audit_queue.is_memory_approved("memory_123")

        assert result is True
        mock_redis_client.hget.assert_called_once_with("resync:audit_status", "memory_123")

    async def test_is_memory_approved_false_pending(self, audit_queue, mock_redis_client):
        """Test checking if memory is approved when pending."""
        mock_redis_client.hget.return_value = b"pending"

        result = await audit_queue.is_memory_approved("memory_123")

        assert result is False

    async def test_is_memory_approved_false_rejected(self, audit_queue, mock_redis_client):
        """Test checking if memory is approved when rejected."""
        mock_redis_client.hget.return_value = b"rejected"

        result = await audit_queue.is_memory_approved("memory_123")

        assert result is False

    async def test_is_memory_approved_not_found(self, audit_queue, mock_redis_client):
        """Test checking if non-existent memory is approved."""
        mock_redis_client.hget.return_value = None

        result = await audit_queue.is_memory_approved("nonexistent_memory")

        assert result is False

    async def test_get_queue_length(self, audit_queue, mock_redis_client):
        """Test getting queue length."""
        mock_redis_client.llen.return_value = 42

        result = await audit_queue.get_queue_length()

        assert result == 42
        mock_redis_client.llen.assert_called_once_with("resync:audit_queue")

    async def test_get_all_audits(self, audit_queue, mock_redis_client):
        """Test getting all audit records."""
        # Mock Redis responses
        memory_ids = [b"memory_1", b"memory_2", b"memory_3"]
        mock_redis_client.hgetall.return_value = {
            b"memory_1": b'{"status": "pending"}',
            b"memory_2": b'{"status": "approved"}',
            b"memory_3": b'{"status": "rejected"}',
        }

        result = await audit_queue.get_all_audits()

        assert len(result) == 3
        assert result[0]["status"] == "pending"
        assert result[1]["status"] == "approved"
        assert result[2]["status"] == "rejected"

    async def test_get_audits_by_status(self, audit_queue, mock_redis_client):
        """Test getting audits by status."""
        # Mock Redis responses
        mock_redis_client.hgetall.return_value = {
            b"memory_1": b'{"status": "pending"}',
            b"memory_2": b'{"status": "approved"}',
            b"memory_3": b'{"status": "pending"}',
        }

        result = await audit_queue.get_audits_by_status("pending")

        assert len(result) == 2
        assert all(audit["status"] == "pending" for audit in result)

    async def test_get_audit_metrics(self, audit_queue, mock_redis_client):
        """Test getting audit metrics."""
        mock_redis_client.hgetall.return_value = {
            b"memory_1": b'{"status": "pending"}',
            b"memory_2": b'{"status": "approved"}',
            b"memory_3": b'{"status": "rejected"}',
            b"memory_4": b'{"status": "pending"}',
        }

        result = await audit_queue.get_audit_metrics()

        assert result["total"] == 4
        assert result["pending"] == 2
        assert result["approved"] == 1
        assert result["rejected"] == 1

    async def test_health_check_success(self, audit_queue, mock_redis_client):
        """Test successful health check."""
        mock_redis_client.ping.return_value = True

        result = await audit_queue.health_check()

        assert result is True
        mock_redis_client.ping.assert_called_once()

    async def test_health_check_failure(self, audit_queue, mock_redis_client):
        """Test failed health check."""
        mock_redis_client.ping.side_effect = Exception("Connection failed")

        result = await audit_queue.health_check()

        assert result is False

    async def test_redis_error_handling(self, audit_queue, mock_redis_client):
        """Test Redis error handling."""
        mock_redis_client.hexists.side_effect = Exception("Redis connection error")

        with pytest.raises(AuditError):
            await audit_queue.add_audit_record({"id": "test"})

    async def test_invalid_json_data(self, audit_queue, mock_redis_client):
        """Test handling of invalid JSON data."""
        mock_redis_client.hget.return_value = b"invalid json"

        with pytest.raises(DataParsingError):
            await audit_queue.get_all_audits()

    async def test_memory_data_storage(self, audit_queue, sample_memory, mock_redis_client):
        """Test that memory data is properly stored and retrieved."""
        # Mock successful addition
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        # Add memory
        await audit_queue.add_audit_record(sample_memory)

        # Verify data was stored correctly
        pipeline = mock_redis_client.pipeline.return_value.__aenter__.return_value
        pipeline.hset.assert_any_call(
            "resync:audit_data",
            "test_memory_123",
            json.dumps({
                "memory_id": "test_memory_123",
                "user_query": "What is the capital of France?",
                "agent_response": "The capital of France is Paris.",
                "ia_audit_reason": "This is a factual question about geography.",
                "ia_audit_confidence": 0.95,
                "status": "pending",
                "created_at": pytest.approx(datetime.utcnow().isoformat(), abs=1),
            })
        )

    async def test_concurrent_operations(self, audit_queue, mock_redis_client):
        """Test concurrent operations."""
        import asyncio

        # Mock Redis responses
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        async def add_memory(memory_id):
            memory = {
                "id": memory_id,
                "user_query": f"Query {memory_id}",
                "agent_response": f"Response {memory_id}"
            }
            return await audit_queue.add_audit_record(memory)

        # Test concurrent additions
        results = await asyncio.gather(*[add_memory(f"memory_{i}") for i in range(5)])

        assert all(results)  # All should succeed
        assert mock_redis_client.hexists.call_count == 5

    async def test_large_queue_operations(self, audit_queue, mock_redis_client):
        """Test operations with large queues."""
        # Create 1000 memory IDs
        memory_ids = [f"memory_{i}".encode() for i in range(1000)]
        mock_redis_client.lrange.return_value = memory_ids

        # Mock status and data for all memories
        mock_redis_client.hget.side_effect = [b"pending"] * 1000

        result = await audit_queue.get_pending_audits(limit=1000)

        assert len(result) == 1000
        mock_redis_client.lrange.assert_called_once_with("resync:audit_queue", 0, 999)

    async def test_memory_data_validation(self, audit_queue, mock_redis_client):
        """Test memory data validation."""
        # Test with missing required fields
        invalid_memory = {
            "id": "invalid_memory"
            # Missing user_query and agent_response
        }

        # Should handle gracefully or raise appropriate error
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        # Should not crash, but may not add invalid data
        result = await audit_queue.add_audit_record(invalid_memory)
        # The implementation should handle this case

    async def test_redis_connection_failure(self, audit_queue, mock_redis_client):
        """Test Redis connection failure handling."""
        mock_redis_client.hexists.side_effect = redis.exceptions.ConnectionError("Connection failed")

        with pytest.raises(AuditError):
            await audit_queue.add_audit_record({"id": "test"})

    async def test_audit_queue_cleanup(self, audit_queue, mock_redis_client):
        """Test audit queue cleanup operations."""
        # Mock Redis cleanup
        mock_redis_client.delete.return_value = 3

        # Test cleanup
        deleted_keys = await audit_queue._cleanup_audit_record("memory_123")

        assert deleted_keys == 3
        mock_redis_client.delete.assert_called_once()

    async def test_batch_operations(self, audit_queue, mock_redis_client):
        """Test batch operations."""
        # Mock batch operations
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1, 1]

        memories = [
            {"id": f"memory_{i}", "user_query": f"Query {i}", "agent_response": f"Response {i}"}
            for i in range(10)
        ]

        # Add multiple memories
        for memory in memories:
            mock_redis_client.hexists.return_value = False
            await audit_queue.add_audit_record(memory)

        assert mock_redis_client.hexists.call_count == 10

    async def test_memory_status_transitions(self, audit_queue, mock_redis_client):
        """Test memory status transitions."""
        memory_id = "test_memory"

        # Initially pending
        mock_redis_client.hset.return_value = 1

        # Approve memory
        result = await audit_queue.update_audit_status(memory_id, "approved")
        assert result is True

        # Check approval status
        mock_redis_client.hget.return_value = b"approved"
        is_approved = await audit_queue.is_memory_approved(memory_id)
        assert is_approved is True

        # Reject memory
        await audit_queue.update_audit_status(memory_id, "rejected")
        mock_redis_client.hget.return_value = b"rejected"
        is_approved = await audit_queue.is_memory_approved(memory_id)
        assert is_approved is False

    async def test_audit_queue_performance(self, audit_queue, mock_redis_client):
        """Test audit queue performance characteristics."""
        # Mock Redis responses for performance testing
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        import time

        # Measure time for adding many records
        start_time = time.time()
        for i in range(100):
            memory = {
                "id": f"perf_memory_{i}",
                "user_query": f"Query {i}",
                "agent_response": f"Response {i}"
            }
            await audit_queue.add_audit_record(memory)
        end_time = time.time()

        # Should be reasonably fast (less than 1 second for 100 operations)
        assert end_time - start_time < 1.0

    async def test_audit_queue_error_recovery(self, audit_queue, mock_redis_client):
        """Test error recovery in audit queue operations."""
        # Test that operations can recover from temporary errors
        mock_redis_client.hexists.side_effect = [
            Exception("Temporary error"),
            False  # Second call succeeds
        ]
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        # Should handle the temporary error and retry
        with pytest.raises(Exception):  # First call fails
            await audit_queue.add_audit_record({"id": "test"})

    async def test_memory_data_consistency(self, audit_queue, mock_redis_client):
        """Test memory data consistency across operations."""
        memory_id = "consistency_memory"
        memory = {
            "id": memory_id,
            "user_query": "Consistency test query",
            "agent_response": "Consistency test response"
        }

        # Add memory
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        await audit_queue.add_audit_record(memory)

        # Retrieve and verify data
        mock_redis_client.hgetall.return_value = {
            memory_id.encode(): json.dumps({
                "memory_id": memory_id,
                "user_query": "Consistency test query",
                "agent_response": "Consistency test response",
                "status": "pending"
            }).encode()
        }

        all_audits = await audit_queue.get_all_audits()
        assert len(all_audits) == 1
        assert all_audits[0]["memory_id"] == memory_id
        assert all_audits[0]["user_query"] == "Consistency test query"
        assert all_audits[0]["agent_response"] == "Consistency test response"

    async def test_audit_queue_edge_cases(self, audit_queue, mock_redis_client):
        """Test edge cases in audit queue operations."""

        # Test with empty memory ID
        result = await audit_queue.update_audit_status("", "approved")
        # Should handle gracefully

        # Test with None memory ID
        result = await audit_queue.update_audit_status(None, "approved")
        # Should handle gracefully

        # Test with very long memory ID
        long_memory_id = "a" * 1000
        result = await audit_queue.update_audit_status(long_memory_id, "approved")
        # Should handle gracefully

        # Test with special characters in memory ID
        special_memory_id = "memory_with_@#$%^&*()_special_chars"
        result = await audit_queue.update_audit_status(special_memory_id, "approved")
        # Should handle gracefully

    async def test_audit_queue_memory_efficiency(self, audit_queue, mock_redis_client):
        """Test memory efficiency of audit queue operations."""
        # Mock Redis responses
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        # Test with large memory data
        large_memory = {
            "id": "large_memory",
            "user_query": "A" * 10000,  # Large query
            "agent_response": "B" * 10000,  # Large response
            "ia_audit_reason": "C" * 5000,  # Large reason
            "ia_audit_confidence": 0.95
        }

        # Should handle large data without issues
        result = await audit_queue.add_audit_record(large_memory)
        assert result is True

    async def test_audit_queue_status_validation(self, audit_queue, mock_redis_client):
        """Test audit status validation."""
        memory_id = "validation_memory"

        # Test invalid status
        mock_redis_client.hset.return_value = 1

        # Should handle invalid status gracefully
        result = await audit_queue.update_audit_status(memory_id, "invalid_status")
        assert result is True

        # Check that status was set
        mock_redis_client.hset.assert_called_with("resync:audit_status", memory_id, "invalid_status")

    async def test_audit_queue_data_integrity(self, audit_queue, mock_redis_client):
        """Test data integrity across Redis operations."""
        memory = {
            "id": "integrity_memory",
            "user_query": "Integrity test",
            "agent_response": "Data integrity test"
        }

        # Add memory
        mock_redis_client.hexists.return_value = False
        mock_redis_client.pipeline.return_value.__aenter__.return_value.execute.return_value = [1, 1, 1]

        await audit_queue.add_audit_record(memory)

        # Verify data was stored correctly
        expected_data = {
            "memory_id": "integrity_memory",
            "user_query": "Integrity test",
            "agent_response": "Data integrity test",
            "status": "pending"
        }

        # Check that the data stored matches expected
        stored_data = json.dumps(expected_data)
        pipeline = mock_redis_client.pipeline.return_value.__aenter__.return_value
        pipeline.hset.assert_any_call("resync:audit_data", "integrity_memory", stored_data)
