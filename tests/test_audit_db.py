"""Tests for resync.core.audit_db module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
import os
import threading
from pathlib import Path

from resync.core.audit_db import (
    get_db_connection,
    initialize_database,
    add_audit_record,
    get_pending_audits,
    update_audit_status,
    delete_audit_record,
    is_memory_approved,
)


class TestAuditDB:
    """Test suite for audit database functions."""

    @pytest.fixture
    def temp_db(self):
        """Use the real database for testing."""
        # Clean the database before each test
        try:
            from resync.core.audit_db import delete_audit_record, get_pending_audits
            # Delete all existing records
            pending = get_pending_audits()
            for record in pending:
                delete_audit_record(record['memory_id'])
        except:
            pass

        yield "audit_queue.db"

    @pytest.fixture
    def sample_memory(self):
        """Sample memory data for testing."""
        import uuid
        return {
            "id": f"test_memory_{uuid.uuid4().hex[:8]}",
            "user_query": "What is the capital of France?",
            "agent_response": "The capital of France is Paris.",
            "ia_audit_reason": "This is a factual question about geography.",
            "ia_audit_confidence": 0.95
        }

    def test_get_db_connection(self):
        """Test database connection establishment."""
        conn = get_db_connection()
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_add_audit_record_success(self, sample_memory):
        """Test successful addition of audit record."""
        result = add_audit_record(sample_memory)

        assert result is not None
        assert isinstance(result, int)

        # Verify record was added
        conn = sqlite3.connect("audit_queue.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_queue WHERE memory_id = ?", (sample_memory["id"],))
        row = cursor.fetchone()

        assert row is not None
        assert row['memory_id'] == sample_memory["id"]
        assert row['user_query'] == sample_memory["user_query"]
        assert row['agent_response'] == sample_memory["agent_response"]
        assert row['status'] == 'pending'

        conn.close()

    def test_get_pending_audits_empty(self):
        """Test getting pending audits when database is empty."""
        audits = get_pending_audits()
        assert isinstance(audits, list)
        # Should be empty after our cleanup
        assert len(audits) == 0

    def test_get_pending_audits_with_data(self, sample_memory):
        """Test getting pending audits with existing data."""
        # Add a pending record
        add_audit_record(sample_memory)

        # Get pending audits
        pending_audits = get_pending_audits()

        assert len(pending_audits) >= 1
        found = False
        for audit in pending_audits:
            if audit['memory_id'] == sample_memory["id"]:
                found = True
                assert audit['status'] == 'pending'
                break
        assert found, f"Memory {sample_memory['id']} not found in pending audits"

    def test_update_audit_status_success(self, sample_memory):
        """Test successful audit status update."""
        # Add a record first
        add_audit_record(sample_memory)

        # Update status
        result = update_audit_status(sample_memory["id"], "approved")
        assert result is True

        # Verify update
        conn = sqlite3.connect("audit_queue.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM audit_queue WHERE memory_id = ?", (sample_memory["id"],))
        row = cursor.fetchone()
        assert row['status'] == 'approved'

        conn.close()

    def test_update_audit_status_not_found(self):
        """Test updating status of non-existent record."""
        result = update_audit_status("non_existent_id", "approved")
        assert result is False

    def test_delete_audit_record_success(self, sample_memory):
        """Test successful audit record deletion."""
        # Add a record first
        add_audit_record(sample_memory)

        # Delete the record
        result = delete_audit_record(sample_memory["id"])
        assert result is True

        # Verify deletion
        conn = sqlite3.connect("audit_queue.db")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_queue WHERE memory_id = ?", (sample_memory["id"],))
        row = cursor.fetchone()
        assert row is None

        conn.close()

    def test_is_memory_approved_true(self, sample_memory):
        """Test checking if memory is approved when it is."""
        # Add and approve a record
        add_audit_record(sample_memory)
        update_audit_status(sample_memory["id"], "approved")

        result = is_memory_approved(sample_memory["id"])
        assert result is True

    def test_is_memory_approved_false_pending(self, sample_memory):
        """Test checking if memory is approved when it's pending."""
        # Add a pending record
        add_audit_record(sample_memory)

        result = is_memory_approved(sample_memory["id"])
        assert result is False

    def test_is_memory_approved_not_found(self):
        """Test checking if non-existent memory is approved."""
        result = is_memory_approved("non_existent_id")
        assert result is False


class TestDatabaseConnection:
    """Test database connection functions."""

    @patch('resync.core.audit_db.DATABASE_PATH')
    def test_get_db_connection(self, mock_path):
        """Test getting database connection."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            mock_path.return_value = Path(tmp.name)
            
            conn = get_db_connection()
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)
            assert conn.row_factory == sqlite3.Row
            conn.close()
            
            # Cleanup
            Path(tmp.name).unlink()

    @patch('resync.core.audit_db.DATABASE_PATH')
    def test_initialize_database(self, mock_path):
        """Test database initialization."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            mock_path.return_value = Path(tmp.name)
            
            # Initialize database
            initialize_database()
            
            # Verify table was created
            conn = sqlite3.connect(tmp.name)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='audit_queue'
            """)
            result = cursor.fetchone()
            conn.close()
            
            assert result is not None
            assert result[0] == 'audit_queue'
            
            # Cleanup
            Path(tmp.name).unlink()


class TestAuditRecords:
    """Test audit record operations."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            temp_path = Path(tmp.name)
            
            with patch('resync.core.audit_db.DATABASE_PATH', temp_path):
                initialize_database()
                yield temp_path
            
            # Cleanup
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass

    def test_add_audit_record_success(self, temp_db):
        """Test successfully adding an audit record."""
        memory = {
            "id": "test_memory_1",
            "user_query": "How to restart a job?",
            "agent_response": "Use the restart command",
            "ia_audit_reason": "Correct procedure",
            "ia_audit_confidence": 0.95
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = add_audit_record(memory)
        
        assert result is not None
        assert isinstance(result, int)

    def test_add_audit_record_duplicate(self, temp_db):
        """Test adding duplicate audit record."""
        memory = {
            "id": "test_memory_duplicate",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add first time - should succeed
            result1 = add_audit_record(memory)
            assert result1 is not None
            
            # Add second time - should return None (duplicate)
            result2 = add_audit_record(memory)
            assert result2 is None

    def test_add_audit_record_minimal_data(self, temp_db):
        """Test adding audit record with minimal required data."""
        memory = {
            "id": "test_memory_minimal",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = add_audit_record(memory)
        
        assert result is not None

    def test_add_audit_record_missing_required_field(self, temp_db):
        """Test adding audit record with missing required field."""
        memory = {
            "id": "test_memory_incomplete",
            "user_query": "Test query"
            # Missing agent_response
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = add_audit_record(memory)
        
        # Should return None due to error
        assert result is None

    def test_get_pending_audits_empty(self, temp_db):
        """Test getting pending audits when none exist."""
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = get_pending_audits()
        
        assert result == []

    def test_get_pending_audits_with_data(self, temp_db):
        """Test getting pending audits with data."""
        memories = [
            {
                "id": "pending_1",
                "user_query": "Query 1",
                "agent_response": "Response 1"
            },
            {
                "id": "pending_2",
                "user_query": "Query 2",
                "agent_response": "Response 2"
            }
        ]
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add test records
            for memory in memories:
                add_audit_record(memory)
            
            # Get pending audits
            result = get_pending_audits()
        
        assert len(result) == 2
        assert all(record["status"] == "pending" for record in result)
        
        # Should be ordered by created_at DESC
        assert result[0]["memory_id"] in ["pending_1", "pending_2"]
        assert result[1]["memory_id"] in ["pending_1", "pending_2"]

    def test_update_audit_status_success(self, temp_db):
        """Test successfully updating audit status."""
        memory = {
            "id": "test_memory_update",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add record
            add_audit_record(memory)
            
            # Update status
            result = update_audit_status("test_memory_update", "approved")
        
        assert result is True

    def test_update_audit_status_not_found(self, temp_db):
        """Test updating status for non-existent record."""
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = update_audit_status("non_existent", "approved")
        
        assert result is False

    def test_delete_audit_record_success(self, temp_db):
        """Test successfully deleting audit record."""
        memory = {
            "id": "test_memory_delete",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add record
            add_audit_record(memory)
            
            # Delete record
            result = delete_audit_record("test_memory_delete")
        
        assert result is True

    def test_delete_audit_record_not_found(self, temp_db):
        """Test deleting non-existent record."""
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = delete_audit_record("non_existent")
        
        assert result is False

    def test_is_memory_approved_true(self, temp_db):
        """Test checking if memory is approved - true case."""
        memory = {
            "id": "test_memory_approved",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add and approve record
            add_audit_record(memory)
            update_audit_status("test_memory_approved", "approved")
            
            # Check if approved
            result = is_memory_approved("test_memory_approved")
        
        assert result is True

    def test_is_memory_approved_false_pending(self, temp_db):
        """Test checking if memory is approved - false case (pending)."""
        memory = {
            "id": "test_memory_pending",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add record (default status is pending)
            add_audit_record(memory)
            
            # Check if approved
            result = is_memory_approved("test_memory_pending")
        
        assert result is False

    def test_is_memory_approved_false_rejected(self, temp_db):
        """Test checking if memory is approved - false case (rejected)."""
        memory = {
            "id": "test_memory_rejected",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add and reject record
            add_audit_record(memory)
            update_audit_status("test_memory_rejected", "rejected")
            
            # Check if approved
            result = is_memory_approved("test_memory_rejected")
        
        assert result is False

    def test_is_memory_approved_not_found(self, temp_db):
        """Test checking if non-existent memory is approved."""
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            result = is_memory_approved("non_existent")
        
        assert result is False

    def test_database_error_handling(self, temp_db):
        """Test error handling for database operations."""
        with patch('resync.core.audit_db.get_db_connection') as mock_conn:
            # Simulate database error
            mock_conn.side_effect = sqlite3.Error("Database error")
            
            memory = {
                "id": "test_memory_error",
                "user_query": "Test query",
                "agent_response": "Test response"
            }
            
            # Should handle error gracefully
            result = add_audit_record(memory)
            assert result is None

    def test_concurrent_operations(self, temp_db):
        """Test concurrent database operations."""
        import threading
        import time
        
        results = []
        
        def add_records(thread_id):
            for i in range(5):
                memory = {
                    "id": f"thread_{thread_id}_record_{i}",
                    "user_query": f"Query from thread {thread_id}",
                    "agent_response": f"Response from thread {thread_id}"
                }
                with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
                    result = add_audit_record(memory)
                    results.append(result)
                time.sleep(0.01)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_records, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should succeed
        assert len([r for r in results if r is not None]) == 15  # 3 threads × 5 records
        
        # Verify records in database
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            pending = get_pending_audits()
            thread_records = [r for r in pending if r["memory_id"].startswith("thread_")]
            assert len(thread_records) == 15

    def test_sql_injection_protection(self, temp_db):
        """Test protection against SQL injection."""
        malicious_memory = {
            "id": "'; DROP TABLE audit_queue; --",
            "user_query": "'; DELETE FROM audit_queue; --",
            "agent_response": "'; UPDATE audit_queue SET status='approved'; --"
        }
        
        with patch('resync.core.audit_db.DATABASE_PATH', temp_db):
            # Add malicious record - should be safely escaped
            result = add_audit_record(malicious_memory)
            assert result is not None
            
            # Verify table still exists and data is properly escaped
            pending = get_pending_audits()
            assert len(pending) >= 1
            
            # Check that malicious content was stored as literal text
            malicious_record = next(
                (r for r in pending if "DROP TABLE" in r["memory_id"]), 
                None
            )
            assert malicious_record is not None