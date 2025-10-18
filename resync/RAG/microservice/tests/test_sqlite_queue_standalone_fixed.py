import sqlite3
import json
import tempfile
import os
from datetime import datetime, timedelta

# Standalone SQLite job queue implementation for testing
class StandaloneSQLiteJobQueue:
    """
    Standalone SQLite job queue for testing (no dependencies)
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.job_timeout_seconds = 3600  # 1 hour default timeout
        self.init_database()

    def init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS job_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    original_filename TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    progress INTEGER DEFAULT 0,
                    message TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    retries INTEGER DEFAULT 0,
                    timeout_at DATETIME
                )
            ''')

            # Create indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_job_queue_timeout ON job_queue(timeout_at)
            ''')
            conn.commit()

    def enqueue_job(self, job_id: str, file_path: str, original_filename: str, metadata: dict = None) -> str:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO job_queue (job_id, file_path, original_filename, metadata, status, progress, message, timeout_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                file_path,
                original_filename,
                json.dumps(metadata) if metadata else None,
                "queued",
                0,
                "Job queued",
                (datetime.now() + timedelta(seconds=self.job_timeout_seconds)).isoformat()
            ))
            conn.commit()
        return job_id

    def get_next_job(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('BEGIN IMMEDIATE')

            cursor = conn.execute('''
                SELECT * FROM job_queue
                WHERE status = ?
                ORDER BY created_at ASC
                LIMIT 1
            ''', ("queued",))

            row = cursor.fetchone()

            if row:
                # Update status to processing
                conn.execute('''
                    UPDATE job_queue
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', ("processing", row[0]))
                conn.commit()

                # Return job as dict
                job = dict(zip([desc[0] for desc in cursor.description], row))
                job['metadata'] = json.loads(job['metadata']) if job['metadata'] else None
                return job

            conn.commit()
            return None

    def update_job_status(self, job_id: str, status: str, progress: int = None, message: str = None) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            update_sql = '''
                UPDATE job_queue
                SET status = ?, updated_at = CURRENT_TIMESTAMP
            '''
            params = [status]

            if progress is not None:
                update_sql += ", progress = ?"
                params.append(progress)

            if message is not None:
                update_sql += ", message = ?"
                params.append(message)

            update_sql += " WHERE job_id = ?"
            params.append(job_id)

            cursor = conn.execute(update_sql, params)
            conn.commit()

            return cursor.rowcount > 0

    def get_job_status(self, job_id: str):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('''
                SELECT job_id, status, progress, message, retries, created_at, updated_at, timeout_at
                FROM job_queue
                WHERE job_id = ?
            ''', (job_id,)).fetchone()

            if row:
                return {
                    "job_id": row[0],
                    "status": row[1],
                    "progress": row[2],
                    "message": row[3],
                    "retries": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "timeout_at": row[7]
                }
            else:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "progress": 0,
                    "message": "Job ID not found"
                }

    def cleanup_expired_jobs(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            expired_jobs = conn.execute('''
                SELECT job_id FROM job_queue
                WHERE status IN (?, ?) AND timeout_at < ?
            ''', ("queued", "processing", datetime.now().isoformat())).fetchall()

            if expired_jobs:
                job_ids = [job[0] for job in expired_jobs]
                conn.execute('''
                    UPDATE job_queue
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE job_id IN ({})
                '''.format(','.join('?' * len(job_ids))),
                ["timeout"] + job_ids)
                conn.commit()

                return len(expired_jobs)

            return 0

    def get_pending_jobs_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute('''
                SELECT COUNT(*) FROM job_queue
                WHERE status IN (?, ?)
            ''', ("queued", "processing")).fetchone()[0]
            return count

    def get_all_jobs(self):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT * FROM job_queue
                ORDER BY created_at ASC
            ''').fetchall()

            jobs = []
            for row in rows:
                job = dict(zip([desc[0] for desc in conn.description], row))
                job['metadata'] = json.loads(job['metadata']) if job['metadata'] else None
                jobs.append(job)
            return jobs


def test_sqlite_job_queue_basic():
    """Test the SQLite job queue functionality"""
    # Create a temporary database for testing
    db_path = tempfile.mktemp(suffix='.db')

    try:
        # Initialize job queue
        queue = StandaloneSQLiteJobQueue(db_path)

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

        print("✓ Basic job queue test passed")

    finally:
        # Clean up temporary database
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # Ignore permission errors on Windows
            pass


def test_sqlite_job_queue_cleanup():
    """Test job cleanup functionality"""
    # Create a temporary database for testing
    db_path = tempfile.mktemp(suffix='.db')

    try:
        # Initialize job queue with very short timeout for testing
        queue = StandaloneSQLiteJobQueue(db_path)
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

        print("✓ Job cleanup test passed")

    finally:
        # Clean up temporary database
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # Ignore permission errors on Windows
            pass


def test_sqlite_job_queue_multiple_jobs():
    """Test multiple jobs in queue"""
    # Create a temporary database for testing
    db_path = tempfile.mktemp(suffix='.db')

    try:
        # Initialize job queue
        queue = StandaloneSQLiteJobQueue(db_path)

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

        print("✓ Multiple jobs test passed")

    finally:
        # Clean up temporary database
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # Ignore permission errors on Windows
            pass


if __name__ == "__main__":
    test_sqlite_job_queue_basic()
    test_sqlite_job_queue_cleanup()
    test_sqlite_job_queue_multiple_jobs()
    print("All SQLite job queue tests passed!")

