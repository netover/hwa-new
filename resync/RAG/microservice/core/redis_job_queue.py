"""
Redis Job Queue Implementation for RAG Microservice

This module implements a persistent job queue using Redis Streams for reliable
job processing with timeout, retry, and TTL mechanisms.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime, timedelta

import redis.asyncio as redis_async
from pydantic import BaseModel

from resync.core.exceptions import FileProcessingError



from resync.core.structured_logger import get_logger
from resync.RAG.microservice.config.settings import settings

logger = get_logger(__name__)

# Redis Streams configuration
REDIS_JOB_STREAM = "rag_jobs"
REDIS_JOB_GROUP = "rag_consumers"
REDIS_JOB_CONSUMER = "rag_processor"
REDIS_JOB_TTL = 3600  # 1 hour in seconds
REDIS_MAX_RETRIES = 3  # Maximum retry attempts


class RAGJob(BaseModel):
    """Job structure for RAG processing"""
    job_id: str
    file_path: str
    filename: str
    metadata: Dict[str, Any] = {}
    status: str = "queued"  # queued, processing, completed, failed
    created_at: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    retry_count: int = 0
    error_message: Optional[str] = None


class RAGJobQueue:
    """
    Redis-based job queue for RAG microservice with timeout, retry, and TTL mechanisms.
    """
    
    def __init__(self):
        """Initialize the Redis job queue"""
        self.redis_client = None
        self.is_connected = False
        
    async def connect(self):
        """Establish connection to Redis"""
        try:
            self.redis_client = redis_async.from_url(settings.REDIS_URL)
            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Connected to Redis job queue")
            
            # Create stream and consumer group if they don't exist
            await self._ensure_stream_and_group()
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise FileProcessingError(f"Redis connection failed: {str(e)}")
    
    async def _ensure_stream_and_group(self):
        """Ensure Redis stream and consumer group exist"""
        try:
            # Create stream if it doesn't exist
            await self.redis_client.xadd(REDIS_JOB_STREAM, {"dummy": "1"}, id="*")
            
            # Create consumer group if it doesn't exist
            try:
                await self.redis_client.xgroup_create(
                    REDIS_JOB_STREAM, 
                    REDIS_JOB_GROUP, 
                    id="0", 
                    mkstream=True
                )
                logger.info(f"Created Redis stream {REDIS_JOB_STREAM} and consumer group {REDIS_JOB_GROUP}")
            except redis_async.exceptions.ResponseError as e:
                # Group already exists, this is expected
                if "BUSYGROUP" not in str(e):
                    raise e
                logger.info(f"Consumer group {REDIS_JOB_GROUP} already exists")
        except Exception as e:
            logger.error(f"Failed to create stream/group: {str(e)}")
            raise FileProcessingError(f"Failed to setup Redis stream/group: {str(e)}")
    
    async def enqueue_job(self, file_path: str, filename: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add job to queue and return job_id
        """
        if not self.is_connected:
            await self.connect()
        
        job_id = str(uuid4())
        job_data = {
            "job_id": job_id,
            "file_path": file_path,
            "filename": filename,
            "metadata": json.dumps(metadata or {}),
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "retry_count": "0",
            "error_message": ""
        }
        
        # Add job to Redis stream
        await self.redis_client.xadd(
            REDIS_JOB_STREAM, 
            job_data, 
            id=job_id
        )
        
        # Set TTL on job key (1 hour)
        await self.redis_client.expire(job_id, REDIS_JOB_TTL)
        
        logger.info(f"Job {job_id} enqueued for processing")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[RAGJob]:
        """
        Query job status
        """
        if not self.is_connected:
            await self.connect()
        
        # Get job data from Redis
        job_data = await self.redis_client.hgetall(job_id)
        
        if not job_data:
            return None
        
        # Convert data to RAGJob model
        job = RAGJob(
            job_id=job_data.get(b"job_id", b"").decode(),
            file_path=job_data.get(b"file_path", b"").decode(),
            filename=job_data.get(b"filename", b"").decode(),
            metadata=json.loads(job_data.get(b"metadata", b"{}")),
            status=job_data.get(b"status", b"queued").decode(),
            created_at=datetime.fromisoformat(job_data.get(b"created_at", b"")),
            last_updated=datetime.fromisoformat(job_data.get(b"last_updated", b"")),
            retry_count=int(job_data.get(b"retry_count", b"0")),
            error_message=job_data.get(b"error_message", b"").decode() if job_data.get(b"error_message") else None
        )
        
        return job
    
    async def process_next_job(self) -> Optional[RAGJob]:
        """
        Process next job from queue (sequential processing)
        Returns job if available, None if queue is empty
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            # Read one job from stream
            # This will block until a job is available
            messages = await self.redis_client.xreadgroup(
                REDIS_JOB_GROUP, 
                REDIS_JOB_CONSUMER, 
                {REDIS_JOB_STREAM: ">"}, 
                count=1, 
                block=1000  # 1 second timeout
            )
            
            if not messages:
                return None
            
            # Extract job data
            stream, message_list = messages[0]
            message_id, job_data = message_list[0]
            
            # Convert job data to RAGJob model
            job = RAGJob(
                job_id=message_id.decode(),
                file_path=job_data[b"file_path"].decode(),
                filename=job_data[b"filename"].decode(),
                metadata=json.loads(job_data[b"metadata"]),
                status=job_data[b"status"].decode(),
                created_at=datetime.fromisoformat(job_data[b"created_at"].decode()),
                last_updated=datetime.fromisoformat(job_data[b"last_updated"].decode()),
                retry_count=int(job_data[b"retry_count"]),
                error_message=job_data[b"error_message"].decode() if b"error_message" in job_data else None
            )
            
            # Update job status to processing
            await self._update_job_status(job.job_id, "processing")
            
            logger.info(f"Processing job {job.job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Error processing next job: {str(e)}")
            return None
    
    async def _update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None):
        """Update job status in Redis"""
        if not self.is_connected:
            await self.connect()
        
        # Update job data
        job_data = {
            "status": status,
            "last_updated": datetime.now().isoformat()
        }
        
        if error_message:
            job_data["error_message"] = error_message
        
        # Update job in Redis
        await self.redis_client.hset(job_id, mapping=job_data)
        
        # Reset TTL
        await self.redis_client.expire(job_id, REDIS_JOB_TTL)
        
        logger.info(f"Job {job_id} status updated to {status}")
    
    async def complete_job(self, job_id: str):
        """Mark job as completed"""
        await self._update_job_status(job_id, "completed")
        
        # Remove job from stream after processing
        await self.redis_client.xack(REDIS_JOB_STREAM, REDIS_JOB_GROUP, job_id)
        
        logger.info(f"Job {job_id} completed successfully")
    
    async def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed"""
        # Check retry count
        job = await self.get_job_status(job_id)
        if job and job.retry_count < REDIS_MAX_RETRIES:
            # Increment retry count and requeue
            new_retry_count = job.retry_count + 1
            await self._update_job_status(job_id, "queued", error_message)
            await self.redis_client.hset(job_id, "retry_count", str(new_retry_count))
            
            logger.info(f"Job {job_id} failed, retry {new_retry_count}/{REDIS_MAX_RETRIES}")
            return
        
        # Max retries reached, mark as failed permanently
        await self._update_job_status(job_id, "failed", error_message)
        await self.redis_client.xack(REDIS_JOB_STREAM, REDIS_JOB_GROUP, job_id)
        
        logger.error(f"Job {job_id} failed permanently after {REDIS_MAX_RETRIES} retries: {error_message}")
    
    async def get_pending_jobs_count(self) -> int:
        """Get number of pending jobs in queue"""
        if not self.is_connected:
            await self.connect()
        
        try:
            # Get stream length
            length = await self.redis_client.xlen(REDIS_JOB_STREAM)
            return length
        except Exception as e:
            logger.error(f"Error getting pending jobs count: {str(e)}")
            return 0
    
    async def cleanup_expired_jobs(self):
        """Clean up expired jobs (TTL expired)"""
        if not self.is_connected:
            await self.connect()
        
        try:
            # Get all job IDs
            job_ids = await self.redis_client.keys("*")
            
            for job_id in job_ids:
                # Check if job has expired
                ttl = await self.redis_client.ttl(job_id)
                if ttl <= 0:
                    # Job has expired, remove it
                    await self.redis_client.delete(job_id)
                    logger.info(f"Cleaned up expired job: {job_id.decode()}")
        except Exception as e:
            logger.error(f"Error cleaning up expired jobs: {str(e)}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Redis job queue connection closed")

# Global instance
rag_job_queue = RAGJobQueue()

# Convenience functions
async def enqueue_rag_job(file_path: str, filename: str, metadata: Dict[str, Any] = None) -> str:
    """Convenience function to enqueue a RAG job"""
    return await rag_job_queue.enqueue_job(file_path, filename, metadata)

async def get_rag_job_status(job_id: str) -> Optional[RAGJob]:
    """Convenience function to get RAG job status"""
    return await rag_job_queue.get_job_status(job_id)

async def process_next_rag_job() -> Optional[RAGJob]:
    """Convenience function to process next RAG job"""
    return await rag_job_queue.process_next_job()

async def complete_rag_job(job_id: str):
    """Convenience function to complete a RAG job"""
    await rag_job_queue.complete_job(job_id)

async def fail_rag_job(job_id: str, error_message: str):
    """Convenience function to fail a RAG job"""
    await rag_job_queue.fail_job(job_id, error_message)

async def get_rag_pending_jobs_count() -> int:
    """Convenience function to get pending jobs count"""
    return await rag_job_queue.get_pending_jobs_count()

async def cleanup_expired_rag_jobs():
    """Convenience function to cleanup expired jobs"""
    await rag_job_queue.cleanup_expired_jobs()
