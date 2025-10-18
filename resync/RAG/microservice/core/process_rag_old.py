"""
RAG Job Processing Logic

This module contains the core logic for processing RAG jobs using the SQLite job queue.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

# Import from local microservice
from .file_ingestor import FileIngestor
from .knowledge_graph_circuit_breaker import CircuitBreakerAsyncKnowledgeGraph
from .sqlite_job_queue import SQLiteJobQueue

# Global job queue instance
_rag_job_queue: Optional[SQLiteJobQueue] = None

from resync.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_rag_job_queue(job_queue: SQLiteJobQueue) -> None:
    """Set the global RAG job queue instance."""
    global _rag_job_queue
    _rag_job_queue = job_queue


async def process_rag_job(job_id: str, file_path: str) -> None:
    """
    Process a RAG job: ingest file and add to knowledge graph.
    This runs asynchronously in the background.
    """
    logger.info(f"Starting RAG job {job_id} for file: {file_path}")

    try:
        # Initialize components
        # In production, these would be injected via dependency injection
        knowledge_graph = CircuitBreakerAsyncKnowledgeGraph()
        file_ingestor = FileIngestor()

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Update job status to processing
        if _rag_job_queue:
            await _rag_job_queue.update_job_status(job_id, "processing", progress=10, message="Starting processing")

        # Ingest file (this will chunk and add to knowledge graph)
        file_path_obj = Path(file_path)
        success = await file_ingestor.ingest_file(file_path_obj)

        if success:
            if _rag_job_queue:
                await _rag_job_queue.update_job_status(job_id, "completed", progress=100, message="File successfully processed and added to knowledge graph")
            logger.info(f"RAG job {job_id} completed successfully")
        else:
            if _rag_job_queue:
                await _rag_job_queue.update_job_status(job_id, "failed", progress=100, message="Failed to process file")
            logger.error(f"RAG job {job_id} failed during ingestion")

    except Exception as e:
        if _rag_job_queue:
            await _rag_job_queue.update_job_status(job_id, "failed", progress=100, message=f"Error processing file: {str(e)}")
        logger.error(f"RAG job {job_id} failed with error: {str(e)}", exc_info=True)

    finally:
        # Clean up temporary file
        try:
            os.remove(file_path)
            logger.info(f"Temporary file {file_path} cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {file_path}: {str(e)}")


async def process_rag_jobs_loop():
    """
    Main loop for processing RAG jobs sequentially.
    This should be run as a background task.
    """
    logger.info("Starting RAG job processing loop")

    while True:
        try:
            # Get next job from queue
            if _rag_job_queue:
                job = await _rag_job_queue.get_next_job()

                if job:
                    # Process the job
                    await process_rag_job(job['job_id'], job['file_path'])

                    # Small delay to prevent tight loop
                    await asyncio.sleep(0.1)
                else:
                    # No jobs available, wait a bit before checking again
                    await asyncio.sleep(1)
            else:
                logger.warning("RAG job queue not initialized, waiting...")
                await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error in RAG job processing loop: {str(e)}", exc_info=True)
            await asyncio.sleep(5)  # Wait longer on error


async def init_rag_processing():
    """
    Initialize RAG job processing.
    This should be called on application startup.
    """
    global _rag_job_queue

    # Initialize SQLite job queue
    _rag_job_queue = SQLiteJobQueue()

    # Clean up any expired jobs
    cleaned_count = await _rag_job_queue.cleanup_expired_jobs()
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} expired jobs on startup")

    # Start the job processing loop in background
    asyncio.create_task(process_rag_jobs_loop())
    logger.info("RAG job processing initialized")


async def get_rag_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a RAG processing job.
    """
    if _rag_job_queue:
        return await _rag_job_queue.get_job_status(job_id)
    else:
        return {
            "job_id": job_id,
            "status": "not_found",
            "progress": 0,
            "message": "Job queue not initialized"
        }


async def enqueue_rag_job(job_id: str, file_path: str, original_filename: str, metadata: Optional[Dict] = None) -> str:
    """
    Enqueue a RAG job for processing.
    """
    if _rag_job_queue:
        return await _rag_job_queue.enqueue_job(job_id, file_path, original_filename, metadata)
    else:
        raise Exception("Job queue not initialized")


# Initialize job status store
# This is now handled by SQLite