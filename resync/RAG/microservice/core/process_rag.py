"""
RAG Job Processing Logic

This module contains the core logic for processing RAG jobs using the SQLite job queue
with sequential processing and detailed logging.
"""

import os
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import from local microservice
from core.sqlite_job_queue import SQLiteJobQueue
from core.processor import process_rag_file_job

# Global job queue instance
_rag_job_queue: Optional[SQLiteJobQueue] = None

from resync.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_rag_job(job_id: str, file_path: str, original_filename: str) -> None:
    """
    Process a RAG job using the new processor with detailed logging.
    This runs asynchronously in the background with progress tracking.
    """
    logger.info(f"[{job_id}] Starting RAG job processing for file: {original_filename}")

    try:
        # Update job status to processing
        if _rag_job_queue:
            await _rag_job_queue.update_job_status(job_id, "processing", progress=5, message="Initializing processor")

        # Process the file using the new RAG processor
        processing_result = await process_rag_file_job(job_id, file_path, original_filename)

        # Update final job status based on processing result
        if processing_result.get("success", False):
            if _rag_job_queue:
                await _rag_job_queue.update_job_status(
                    job_id,
                    "completed",
                    progress=100,
                    message=f"Successfully processed {processing_result.get('chunks_created', 0)} chunks"
                )
            logger.info(f"[{job_id}] RAG processing completed successfully")
        else:
            error_msg = "; ".join(processing_result.get("errors", ["Unknown error"]))
            if _rag_job_queue:
                await _rag_job_queue.update_job_status(
                    job_id,
                    "failed",
                    progress=100,
                    message=f"Processing failed: {error_msg}"
                )
            logger.error(f"[{job_id}] RAG processing failed: {error_msg}")

    except Exception as e:
        if _rag_job_queue:
            await _rag_job_queue.update_job_status(
                job_id,
                "failed",
                progress=100,
                message=f"Unexpected error: {str(e)}"
            )
        logger.error(f"[{job_id}] Unexpected error during RAG processing: {e}", exc_info=True)


async def process_rag_jobs_loop():
    """
    Main loop for processing RAG jobs sequentially.
    This should be run as a background task.
    """
    logger.info("Starting RAG job processing loop (sequential processing)")

    while True:
        try:
            # Get next job from queue
            if _rag_job_queue:
                job = await _rag_job_queue.get_next_job()

                if job:
                    logger.info(f"Processing job {job['job_id']} for file: {job['original_filename']}")

                    # Process the job using the new processor
                    await process_rag_job(job['job_id'], job['file_path'], job['original_filename'])

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
    logger.info("RAG job processing initialized with sequential processing")


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
# This is now handled by SQLite with persistence
