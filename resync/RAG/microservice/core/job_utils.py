"""
RAG Job Utility Functions

This module contains utility functions for RAG job processing that are shared between
modules to avoid circular imports.
"""

from typing import Dict, Any
from .redis_job_queue import RAGJobQueue

async def get_rag_job_status(job_id: str, job_queue: RAGJobQueue) -> Dict[str, Any]:
    """
    Get the status of a RAG processing job.
    
    Args:
        job_id: The job identifier
        job_queue: The RAG job queue instance
    """
    return await job_queue.get_job_status(job_id)