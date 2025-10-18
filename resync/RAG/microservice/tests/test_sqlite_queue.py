import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add the microservice directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from resync.RAG.microservice.core.sqlite_job_queue import SQLiteJobQueue


def test_sqlite_job_queue_basic():
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


def test_sqlite_job_queue_cleanup():
    """Test job cleanup functionality"""
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # Initialize job queue with very short timeout for testing
        queue = SQLiteJobQueue(db_path)

        # Manually set a very short timeout for testing
        queue.job_timeout_seconds = 0.001  # Very short timeout

        # Test enqueue job
        job_id = "cleanup-test-job"
        file_path = "/tmp/cleanup_test_file.txt"
        filename = "cleanup_test_file.txt"

        queue.enqueue_job(job_id, file_path, filename)

        # Wait for timeout
        import time
        time.sleep(0.01)

        # Test cleanup expired jobs
        cleaned = queue.cleanup_expired_jobs()
        assert cleaned == 1  # Should clean 1 expired job

        # Verify job was cleaned up (marked as timeout)
        status = queue.get_job_status(job_id)
        assert status["status"] == "timeout"

    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_sqlite_job_queue_multiple_jobs():
    """Test multiple jobs in queue"""
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        # Initialize job queue
        queue = SQLiteJobQueue(db_path)

        # Enqueue multiple jobs
        jobs = []
        for i in range(3):
            job_id = f"multi-job-{i}"
            file_path = f"/tmp/multi_file_{i}.txt"
            filename = f"multi_file_{i}.txt"

            result_id = queue.enqueue_job(job_id, file_path, filename)
            assert result_id == job_id
            jobs.append(job_id)

        # Check pending count
        count = queue.get_pending_jobs_count()
        assert count == 3

        # Process all jobs
        processed_jobs = []
        for _ in range(3):
            job = queue.get_next_job()
            assert job is not None
            processed_jobs.append(job["job_id"])

            # Mark as completed
            queue.update_job_status(job["job_id"], "completed")

        # Verify all jobs were processed
        assert len(processed_jobs) == 3
        assert set(processed_jobs) == set(jobs)

        # Check pending count is now 0
        count = queue.get_pending_jobs_count()
        assert count == 0

    finally:
        # Clean up temporary database
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == "__main__":
    test_sqlite_job_queue_basic()
    test_sqlite_job_queue_cleanup()
    test_sqlite_job_queue_multiple_jobs()
    print("All SQLite job queue tests passed!")
