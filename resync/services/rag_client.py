"""
RAG Service Client for API Gateway

This module provides a client to communicate with the standalone RAG microservice.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import httpx
from pydantic import BaseModel

from resync.core.structured_logger import get_logger
from resync.settings import settings

logger = get_logger(__name__)


class RAGJobStatus(BaseModel):
    """Model for RAG job status response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: Optional[int] = None
    message: Optional[str] = None


class RAGUploadResponse(BaseModel):
    """Model for RAG upload response"""
    job_id: str
    filename: str
    status: str


class RAGServiceClient:
    """
    Client to communicate with the RAG microservice.
    
    Implements:
    - HTTP client with retry logic
    - Circuit breaker for protection
    - Timeout configuration
    - Error handling
    """
    
    def __init__(self):
        """Initialize the RAG service client"""
        self.rag_service_url = settings.RAG_SERVICE_URL
        self.timeout = httpx.Timeout(timeout=30.0, connect=10.0)
        self.max_retries = 3
        self.retry_backoff = 1.0  # seconds
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            name="rag_service",
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=httpx.RequestError
        )
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5
            )
        )
        
        logger.info("RAGServiceClient initialized")
    
    async def enqueue_file(self, file: Any) -> str:
        """
        Enqueue a file for RAG processing.
        
        Args:
            file: UploadFile object from FastAPI
            
        Returns:
            str: Generated job_id
            
        Raises:
            Exception: If upload fails after retries
        """
        if not self.rag_service_url:
            raise Exception("RAG_SERVICE_URL not configured")
        
        # Use circuit breaker
        async with self.circuit_breaker:
            for attempt in range(self.max_retries):
                try:
                    # Prepare file for upload
                    files = {"file": (file.filename, file.file, file.content_type)}
                    
                    # Make request to RAG microservice
                    response = await self.http_client.post(
                        f"{self.rag_service_url}/api/v1/upload",
                        files=files
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_id = data["job_id"]
                        logger.info(f"File {file.filename} enqueued successfully with job_id: {job_id}")
                        return job_id
                    else:
                        logger.error(f"RAG service returned {response.status_code}: {response.text}")
                        
                except httpx.RequestError as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to enqueue file after {self.max_retries} attempts")
                        raise Exception(f"Failed to enqueue file after {self.max_retries} attempts: {str(e)}")
                    
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
                
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Unexpected error after {self.max_retries} attempts: {str(e)}")
                    
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
        
        raise Exception("Failed to enqueue file")
    
    async def get_job_status(self, job_id: str) -> RAGJobStatus:
        """
        Get the status of a RAG processing job.
        
        Args:
            job_id: The job identifier
            
        Returns:
            RAGJobStatus: Job status information
            
        Raises:
            Exception: If job status cannot be retrieved
        """
        if not self.rag_service_url:
            raise Exception("RAG_SERVICE_URL not configured")
        
        # Use circuit breaker
        async with self.circuit_breaker:
            for attempt in range(self.max_retries):
                try:
                    response = await self.http_client.get(
                        f"{self.rag_service_url}/api/v1/jobs/{job_id}"
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_status = RAGJobStatus(**data)
                        logger.info(f"Retrieved status for job {job_id}: {job_status.status}")
                        return job_status
                    elif response.status_code == 404:
                        logger.warning(f"Job {job_id} not found")
                        return RAGJobStatus(
                            job_id=job_id,
                            status="not_found",
                            progress=0,
                            message="Job ID not found"
                        )
                    else:
                        logger.error(f"RAG service returned {response.status_code}: {response.text}")
                        
                except httpx.RequestError as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to get job status after {self.max_retries} attempts")
                        raise Exception(f"Failed to get job status after {self.max_retries} attempts: {str(e)}")
                    
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
                
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Unexpected error after {self.max_retries} attempts: {str(e)}")
                    
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt))
        
        raise Exception("Failed to get job status")


class CircuitBreaker:
    """
    Circuit breaker implementation to protect against RAG service failures.
    
    Implements:
    - Closed state: Normal operation
    - Open state: Fail fast when failures exceed threshold
    - Half-open state: Test service availability after recovery timeout
    """
    
    def __init__(self, name: str, failure_threshold: int, recovery_timeout: int, expected_exception: type):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting to recover
            expected_exception: Exception type that counts as a failure
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
        logger.info(f"CircuitBreaker {name} initialized with threshold={failure_threshold}, timeout={recovery_timeout}")
    
    async def __aenter__(self):
        """Enter context manager"""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time and (
                (self.last_failure_time + self.recovery_timeout) < asyncio.get_event_loop().time()
            ):
                self.state = "half-open"
                logger.info(f"CircuitBreaker {self.name} transitioning to half-open")
            else:
                raise Exception(f"RAG service is unavailable (circuit open)")
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        if exc_type and issubclass(exc_type, self.expected_exception):
            self.failure_count += 1
            self.last_failure_time = asyncio.get_event_loop().time()
            logger.warning(f"CircuitBreaker {self.name} failure #{self.failure_count}")
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"CircuitBreaker {self.name} opened after {self.failure_count} failures")
        elif exc_type is None:
            # Success - reset failure count if in half-open state
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                logger.info(f"CircuitBreaker {self.name} closed after successful request")
        
        return False  # Don't suppress exceptions

# Global instance
rag_client = RAGServiceClient()
"""Global RAG service client instance"""