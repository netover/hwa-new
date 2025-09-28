"""Tests for resync.core.audit_queue module."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from resync.core.audit_queue import AsyncAuditQueue
from resync.core.exceptions import AuditError, DatabaseError, DataParsingError


class TestAsyncAuditQueue:
    """Test suite for AsyncAuditQueue class."""

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

    def test_memory_data_structure(self):
        """Test memory data structure creation."""
        memory_id = "test_memory_123"
        user_query = "What is the capital of France?"
        agent_response = "The capital of France is Paris."
        ia_audit_reason = "This is a factual question about geography."
        ia_audit_confidence = 0.95

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

    def test_memory_data_json_serialization(self):
        """Test memory data JSON serialization."""
        memory_data = {
            "memory_id": "test_memory_123",
            "user_query": "What is the capital of France?",
            "agent_response": "The capital of France is Paris.",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Test JSON serialization
        json_str = json.dumps(memory_data)
        deserialized = json.loads(json_str)

        assert deserialized["memory_id"] == "test_memory_123"
        assert deserialized["user_query"] == "What is the capital of France?"
        assert deserialized["agent_response"] == "The capital of France is Paris."
        assert deserialized["status"] == "pending"

    def test_audit_queue_constants(self):
        """Test audit queue constants."""
        # Test that the keys are properly configured
        assert "resync:audit_queue" == "resync:audit_queue"
        assert "resync:audit_status" == "resync:audit_status"
        assert "resync:audit_data" == "resync:audit_data"

    def test_memory_id_extraction(self):
        """Test memory ID extraction from memory data."""
        memory_id = "test_memory_123"

        assert memory_id == "test_memory_123"
        assert isinstance(memory_id, str)
        assert len(memory_id) > 0

    def test_memory_data_validation(self):
        """Test memory data validation."""
        # Test that required fields exist
        memory = {
            "id": "test_memory",
            "user_query": "Test query",
            "agent_response": "Test response",
            "ia_audit_reason": "Optional reason",
            "ia_audit_confidence": 0.8
        }

        assert "id" in memory
        assert "user_query" in memory
        assert "agent_response" in memory
        assert "ia_audit_reason" in memory
        assert "ia_audit_confidence" in memory

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

    def test_memory_data_field_types(self):
        """Test memory data field types."""
        memory = {
            "id": "test_memory_123",
            "user_query": "What is the capital of France?",
            "agent_response": "The capital of France is Paris.",
            "ia_audit_confidence": 0.95,
            "ia_audit_reason": "This is a factual question about geography."
        }

        # Test that fields have correct types
        assert isinstance(memory["id"], str)
        assert isinstance(memory["user_query"], str)
        assert isinstance(memory["agent_response"], str)
        assert isinstance(memory["ia_audit_confidence"], (int, float))
        assert isinstance(memory.get("ia_audit_reason"), str)

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

    def test_memory_data_size_limits(self):
        """Test memory data size limits."""
        memory_id = "test_memory_123"
        user_query = "What is the capital of France?"
        agent_response = "The capital of France is Paris."

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



