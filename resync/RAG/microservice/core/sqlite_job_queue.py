import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

JOB_STATUS_QUEUED = "queued"
JOB_STATUS_PROCESSING = "processing"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"
JOB_STATUS_TIMEOUT = "timeout"
JOB_STATUS_NOT_FOUND = "not_found"

class SQLiteJobQueue:
    def __init__(self, db_path=None):
        self.db_path = db_path or "job_queue.db"
        self.lock = threading.Lock()
        self.init_database()
        logger.info(f"SQLiteJobQueue initialized with DB: {self.db_path}")

    def init_database(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS job_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT UNIQUE NOT NULL,
                        file_path TEXT NOT NULL,
                        original_filename TEXT,
                        status TEXT NOT NULL DEFAULT 
queued,
                        progress INTEGER DEFAULT 0,
                        message TEXT,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        retries INTEGER DEFAULT 0,
                        timeout_at DATETIME
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_job_queue_timeout ON job_queue(timeout_at)
                """)
                conn.commit()
            logger.info("SQLite database schema initialized.")

    async def enqueue_job(self, job_id: str, file_path: str, original_filename: str, metadata=None):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO job_queue (job_id, file_path, original_filename, metadata, status, progress, message, timeout_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_id,
                    file_path,
                    original_filename,
                    json.dumps(metadata) if metadata else None,
                    JOB_STATUS_QUEUED,
                    0,
                    "Job queued",
                    (datetime.now() + timedelta(seconds=3600)).isoformat()
                ))
                conn.commit()
            logger.info(f"Job {job_id} enqueued.")
            return job_id

    async def get_next_job(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('BEGIN IMMEDIATE')
                self._handle_expired_processing_jobs(conn)
                
                cursor = conn.execute("""
                    SELECT * FROM job_queue
                    WHERE status = ?
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (JOB_STATUS_QUEUED,))
                row = cursor.fetchone()

                if row:
                    job_id = row[1]
                    conn.execute("""
                        UPDATE job_queue
                        SET status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    """, (JOB_STATUS_PROCESSING, job_id))
                    conn.commit()

                    col_names = [description[0] for description in cursor.description]
                    job = dict(zip(col_names, row))
                    job[metadata] = json.loads(job[metadata]) if job[metadata] else None
                    logger.info(f"Job {job_id} retrieved for processing.")
                    return job
                else:
                    conn.commit()
                    return None

    def _handle_expired_processing_jobs(self, conn):
        current_time = datetime.now().isoformat()
        expired_jobs = conn.execute("""
            SELECT job_id, retries FROM job_queue
            WHERE status = ? AND timeout_at < ?
        """, (JOB_STATUS_PROCESSING, current_time)).fetchall()

        for job_id, retries in expired_jobs:
            if retries < 3:  # max_retries hardcoded for simplicity
                conn.execute("""
                    UPDATE job_queue
                    SET status = ?, retries = ?, updated_at = CURRENT_TIMESTAMP,
                    message = ?
                    WHERE job_id = ?
                """, ("retrying", retries + 1, f"Job timed out, retrying (attempt {retries + 1}/3)", job_id))
            else:
                conn.execute("""
                    UPDATE job_queue
                    SET status = ?, updated_at = CURRENT_TIMESTAMP, message = ?
                    WHERE job_id = ?
                """, (JOB_STATUS_FAILED, "Job timed out and exceeded max retries", job_id))

    async def update_job_status(self, job_id: str, status: str, progress=None, message=None):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                update_sql = """
                    UPDATE job_queue
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                """
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

    async def get_job_status(self, job_id: str):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("""
                    SELECT job_id, status, progress, message, retries, created_at, updated_at, timeout_at, original_filename, file_path
                    FROM job_queue
                    WHERE job_id = ?
                """, (job_id,)).fetchone()

                if row:
                    return dict(row)
                else:
                    return {
                        "job_id": job_id,
                        "status": JOB_STATUS_NOT_FOUND,
                        "progress": 0,
                        "message": "Job ID not found"
                    }

    async def cleanup_expired_jobs(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                current_time = datetime.now().isoformat()
                cursor = conn.execute("""
                    SELECT job_id FROM job_queue
                    WHERE status IN (?, ?) AND timeout_at < ?
                """, (JOB_STATUS_QUEUED, JOB_STATUS_PROCESSING, current_time))
                expired_jobs = cursor.fetchall()

                if expired_jobs:
                    job_ids = [job[0] for job in expired_jobs]
                    conn.execute("""
                        UPDATE job_queue
                        SET status = ?, updated_at = CURRENT_TIMESTAMP, message = ?
                        WHERE job_id IN ({})
                    """.format(','.join('?' * len(job_ids))),
                    [JOB_STATUS_TIMEOUT, "Job timed out"] + job_ids)
                    conn.commit()
                    return len(expired_jobs)
                return 0

    async def get_pending_jobs_count(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                count = conn.execute("""
                    SELECT COUNT(*) FROM job_queue
                    WHERE status IN (?, ?)
                """, (JOB_STATUS_QUEUED, JOB_STATUS_PROCESSING)).fetchone()[0]
                return count

    async def get_all_jobs(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT * FROM job_queue
                    ORDER BY created_at ASC
                """).fetchall()

                jobs = []
                for row in rows:
                    job = dict(row)
                    job[metadata] = json.loads(job[metadata]) if job[metadata] else None
                    jobs.append(job)
                return jobs
