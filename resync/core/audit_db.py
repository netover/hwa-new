import logging
import sqlite3
from typing import Any, Dict, List, Optional

from resync.settings import settings

logger = logging.getLogger(__name__)

DATABASE_PATH = settings.BASE_DIR / "audit_queue.db"


def get_db_connection() -> sqlite3.Connection:
    """Establishes and returns a TWS-optimized SQLite database connection."""
    conn = sqlite3.connect(DATABASE_PATH)

    # TWS-specific SQLite optimizations
    conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
    conn.execute("PRAGMA synchronous = NORMAL")  # Better performance
    conn.execute("PRAGMA cache_size = 10000")  # 10MB cache
    conn.execute("PRAGMA temp_store = memory")  # Memory temp tables
    conn.execute("PRAGMA foreign_keys = ON")  # Data integrity

    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def initialize_database() -> None:
    """Initializes the database, creating the audit_queue table if it doesn't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
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
        """
        )
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
            cursor.execute(
                """
                INSERT INTO audit_queue (
                    memory_id, user_query, agent_response,
                    ia_audit_reason, ia_audit_confidence, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    memory["id"],
                    memory["user_query"],
                    memory["agent_response"],
                    memory.get("ia_audit_reason"),
                    memory.get("ia_audit_confidence"),
                    "pending",
                ),
            )
            conn.commit()
            logger.debug("Added memory %s to audit queue.", memory["id"])
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.debug(
                "Memory %s already exists in audit queue. Skipping.", memory["id"]
            )
            return None
        except Exception as e:
            logger.error(
                "Error adding memory %s to audit queue: %s",
                memory.get("id"),
                e,
                exc_info=True,
            )
            return None


def add_audit_records_batch(memories: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Batch insert multiple audit records for better performance.

    Args:
        memories: List of memory dictionaries

    Returns:
        List of record IDs (None for duplicates)
    """
    if not memories:
        return []

    with get_db_connection() as conn:
        cursor = conn.cursor()
        record_ids = []

        for memory in memories:
            try:
                cursor.execute(
                    """
                    INSERT INTO audit_queue (
                        memory_id, user_query, agent_response,
                        ia_audit_reason, ia_audit_confidence, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        memory["id"],
                        memory["user_query"],
                        memory["agent_response"],
                        memory.get("ia_audit_reason"),
                        memory.get("ia_audit_confidence"),
                        "pending",
                    ),
                )
                record_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                logger.debug(
                    "Memory %s already exists in audit queue. Skipping.", memory["id"]
                )
                record_ids.append(None)
            except Exception as e:
                logger.error(
                    "Error adding memory %s to audit queue: %s",
                    memory.get("id"),
                    e,
                    exc_info=True,
                )
                record_ids.append(None)

        conn.commit()
        logger.info(
            "Batch inserted %d audit records",
            len([id for id in record_ids if id is not None]),
        )
        return record_ids


def get_pending_audits() -> List[Dict[str, Any]]:
    """
    Retrieves all memories currently pending review.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM audit_queue WHERE status = 'pending' ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_audit_status(memory_id: str, status: str) -> bool:
    """
    Updates the status of an audit record.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE audit_queue
            SET status = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE memory_id = ?
        """,
            (status, memory_id),
        )
        conn.commit()
        if cursor.rowcount > 0:
            logger.info("Updated memory %s status to %s.", memory_id, status)
            return True
        logger.warning("Memory %s not found for status update.", memory_id)
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
            logger.info("Deleted memory %s from audit queue.", memory_id)
            return True
        logger.warning("Memory %s not found for deletion from audit queue.", memory_id)
        return False


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
        cursor.execute(
            "SELECT status FROM audit_queue WHERE memory_id = ?", (memory_id,)
        )
        row = cursor.fetchone()
        return row is not None and row["status"] == "approved"

        return False


# Initialize the database on module import
initialize_database()
