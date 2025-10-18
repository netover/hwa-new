"""
RAG Service Processor

This module implements the main RAG processing logic for handling file uploads
and performing retrieval-augmented generation.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.file_ingestor import FileIngestor
from core.vector_store import VectorStore
from core.sqlite_job_queue import SQLiteJobQueue
from config.settings import settings

logger = logging.getLogger(__name__)

class RAGServiceProcessor:
    """
    Main processor for RAG operations.
    """

    def __init__(self):
        """Initialize the RAG processor."""
        self.file_ingestor = FileIngestor()
        self.vector_store = VectorStore()
        self.job_queue = SQLiteJobQueue()
        logger.info("RAGServiceProcessor initialized")

    async def process_rag_file_job(self, job_id: str, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Process a single RAG file job.

        Args:
            job_id: Job identifier
            file_path: Path to the file to process
            original_filename: Original filename

        Returns:
            Processing result dictionary
        """
        try:
            logger.info(f"Processing file {original_filename} for job {job_id}")

            # Ingest the file
            file_path_obj = Path(file_path)
            success = await self.file_ingestor.ingest_file(file_path_obj)

            if success:
                # Update job status to completed
                await self.job_queue.update_job_status(
                    job_id, "completed", progress=100,
                    message=f"Successfully processed {original_filename}"
                )
                logger.info(f"Successfully processed job {job_id}")
                return {
                    "success": True,
                    "job_id": job_id,
                    "chunks_created": 1,  # Placeholder
                    "message": f"File {original_filename} processed successfully"
                }
            else:
                # Update job status to failed
                await self.job_queue.update_job_status(
                    job_id, "failed", progress=100,
                    message=f"Failed to process {original_filename}"
                )
                logger.error(f"Failed to process job {job_id}")
                return {
                    "success": False,
                    "job_id": job_id,
                    "errors": ["File ingestion failed"],
                    "message": f"Failed to process {original_filename}"
                }

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            await self.job_queue.update_job_status(
                job_id, "failed", progress=100,
                message=f"Processing error: {str(e)}"
            )
            return {
                "success": False,
                "job_id": job_id,
                "errors": [str(e)],
                "message": f"Processing error: {str(e)}"
            }

    async def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar content in the vector store.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of search results
        """
        try:
            results = await self.vector_store.search_similar(query, top_k=top_k)
            logger.info(f"Search completed for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        try:
            pending_count = await self.job_queue.get_pending_jobs_count()
            return {
                "vector_store_type": "FAISS",
                "total_documents": 0,  # Placeholder
                "pending_jobs": pending_count,
                "status": "operational"
            }
        except Exception as e:
            logger.error(f"Failed to get processing stats: {str(e)}")
            return {
                "vector_store_type": "unknown",
                "total_documents": 0,
                "pending_jobs": 0,
                "status": "error",
                "error": str(e)
            }

# Convenience function for job processing
async def process_rag_file_job(job_id: str, file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    Convenience function to process a RAG file job.
    """
    processor = RAGServiceProcessor()
    return await processor.process_rag_file_job(job_id, file_path, original_filename)
