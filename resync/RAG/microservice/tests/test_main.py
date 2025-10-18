import pytest
import asyncio
import tempfile
import os
from fastapi.testclient import TestClient
from resync.RAG.microservice.main import app
from resync.RAG.microservice.core.sqlite_job_queue import SQLiteJobQueue

client = TestClient(app)

def test_read_main():
    response = client.get("/api/v1/status")
    assert response.status_code == 404  # No status endpoint defined yet

def test_health_check():
    # This would test the health endpoint when implemented
    pass

def test_sqlite_job_queue():
    """Test the SQLite job queue functionality"""
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # Initialize job queue
        queue = SQLiteJobQueue(db_path)

        # Test enqueue job
        job_id = "test-job-123"
        file_path = "/tmp/test_file.txt"
        filename = "test_file.txt"

        result_id = queue.enqueue_job(job_id, file_path, filename)
        assert result_id == job_id

        # Test get job status
        status = queue.get_job_status(job_id)
        assert status["job_id"] == job_id
        assert status["status"] == "queued"

        # Test get next job
        job = queue.get_next_job()
        assert job is not None
        assert job["job_id"] == job_id
        assert job["file_path"] == file_path

        # Test update job status
        success = queue.update_job_status(job_id, "completed", progress=100, message="Test completed")
        assert success

        # Verify status was updated
        status = queue.get_job_status(job_id)
        assert status["status"] == "completed"
        assert status["progress"] == 100

        # Test get pending jobs count
        count = queue.get_pending_jobs_count()
        assert count == 0  # No pending jobs after completion

    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)

@pytest.mark.asyncio
async def test_sqlite_job_queue_async():
    """Test async operations of SQLite job queue"""
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # Initialize job queue
        queue = SQLiteJobQueue(db_path)

        # Test enqueue job
        job_id = "async-test-job-456"
        file_path = "/tmp/async_test_file.txt"
        filename = "async_test_file.txt"

        result_id = queue.enqueue_job(job_id, file_path, filename)
        assert result_id == job_id

        # Test cleanup expired jobs (should not clean anything since job is fresh)
        cleaned = queue.cleanup_expired_jobs()
        assert cleaned == 0

        # Test get all jobs
        jobs = queue.get_all_jobs()
        assert len(jobs) == 1
        assert jobs[0]["job_id"] == job_id

    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)