import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from resync.settings import settings

logger = logging.getLogger(__name__)

DATABASE_PATH = settings.BASE_DIR / "audit_queue.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def initialize_database():
    """Initializes the database, creating the audit_queue table if it doesn't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT NOT NULL UNIQUE,
                user_query TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                ia_audit_reason TEXT,
                ia_audit_confidence REAL,
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP
            );
        """)
        conn.commit()
    logger.info(f"Database initialized at {DATABASE_PATH}")

def add_audit_record(memory: Dict[str, Any]) -> Optional[int]:
    """
    Adds a new memory to the audit queue for review.
    Returns the ID of the new record or None if already exists.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO audit_queue (
                    memory_id, user_query, agent_response, 
                    ia_audit_reason, ia_audit_confidence, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                memory['id'],
                memory['user_query'],
                memory['agent_response'],
                memory.get('ia_audit_reason'),
                memory.get('ia_audit_confidence'),
                'pending'
            ))
            conn.commit()
            logger.info(f"Added memory {memory['id']} to audit queue.")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Memory {memory['id']} already exists in audit queue. Skipping.")
            return None
        except Exception as e:
            logger.error(f"Error adding memory {memory.get('id')} to audit queue: {e}", exc_info=True)
            return None

def get_pending_audits() -> List[Dict[str, Any]]:
    """
    Retrieves all memories currently pending review.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_queue WHERE status = 'pending' ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def update_audit_status(memory_id: str, status: str) -> bool:
    """
    Updates the status of an audit record.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE audit_queue
            SET status = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE memory_id = ?
        """, (status, memory_id))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Updated memory {memory_id} status to {status}.")
            return True
        logger.warning(f"Memory {memory_id} not found for status update.")
        return False

def delete_audit_record(memory_id: str) -> bool:
    """
    Deletes an audit record from the queue.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_queue WHERE memory_id = ?", (memory_id,))
        conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Deleted memory {memory_id} from audit queue.")
            return True
        logger.warning(f"Memory {memory_id} not found for deletion from audit queue.")
def is_memory_approved(memory_id: str) -> bool:
    """
    Checks if a memory has been approved by an admin.

    Args:
        memory_id: The ID of the memory to check.

    Returns:
        True if the memory is approved, False otherwise.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM audit_queue WHERE memory_id = ?", (memory_id,))
        row = cursor.fetchone()
        return row is not None and row['status'] == 'approved'

        return False

# Initialize the database on module import
initialize_database()