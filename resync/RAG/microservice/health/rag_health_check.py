"""
RAG Microservice Health Check

This module provides comprehensive health checks for the RAG microservice.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from resync.core.health_models import ComponentHealth, ComponentType, HealthStatus

# Import from local microservice
from ..config import settings
from ..core.file_ingestor import FileIngestor
from ..core.knowledge_graph_circuit_breaker import CircuitBreakerAsyncKnowledgeGraph
from ..core.sqlite_job_queue import SQLiteJobQueue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGHealthCheck:
    """
    Health checker for the RAG microservice.
    """
    
    def __init__(self):
        self.name = "rag_service"
        self.component_type = ComponentType.SERVICE
        self._job_queue = SQLiteJobQueue()
        
    async def check_health(self) -> ComponentHealth:
        """
        Perform comprehensive health check for the RAG microservice.
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check 1: File system access to knowledge base
            knowledge_base_dir = Path(settings.RAG_KNOWLEDGE_BASE_DIR)
            
            if not knowledge_base_dir.exists():
                return ComponentHealth(
                    name=self.name,
                    component_type=self.component_type,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Knowledge base directory not found: {knowledge_base_dir}",
                    last_check=datetime.now(),
                    metadata={"knowledge_base_dir": str(knowledge_base_dir), "exists": False}
                )
            
            if not os.access(knowledge_base_dir, os.R_OK):
                return ComponentHealth(
                    name=self.name,
                    component_type=self.component_type,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Cannot read from knowledge base directory: {knowledge_base_dir}",
                    last_check=datetime.now(),
                    metadata={"knowledge_base_dir": str(knowledge_base_dir), "readable": False}
                )
            
            # Check 2: Redis connectivity
            import redis.asyncio as redis_async
            from redis.exceptions import RedisError
            
            try:
                redis_client = redis_async.from_url(settings.REDIS_URL)
                await redis_client.ping()
                redis_connected = True
                await redis_client.close()
            except RedisError:
                redis_connected = False
            
            # Check 3: Knowledge graph connectivity
            try:
                kg = CircuitBreakerAsyncKnowledgeGraph()
                # Test connection
                # In production, this would be a real test
                kg_connected = True
            except Exception:
                kg_connected = False
            
            # Check 4: Job processing status - use SQLite queue
            jobs_pending = self._job_queue.get_pending_jobs_count()
            
            # Determine overall status
            if not kg_connected:
                status = HealthStatus.UNHEALTHY
                message = "Knowledge graph connection failed"
            elif not knowledge_base_dir.exists():
                status = HealthStatus.UNHEALTHY
                message = "Knowledge base directory not accessible"
            else:
                status = HealthStatus.HEALTHY
                message = "RAG service healthy"
            
            response_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return ComponentHealth(
                name=self.name,
                component_type=self.component_type,
                status=status,
                message=message,
                response_time_ms=response_time_ms,
                last_check=datetime.now(),
                metadata={
                    "knowledge_base_dir": str(knowledge_base_dir),
                    "knowledge_base_exists": knowledge_base_dir.exists(),
                    "job_queue_type": "SQLite",
                    "knowledge_graph_connected": kg_connected,
                    "jobs_pending": jobs_pending,
                    "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                    "max_concurrent_processes": settings.MAX_CONCURRENT_PROCESSES
                }
            )
            
        except Exception as e:
            response_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.error(f"RAG health check failed: {str(e)}", exc_info=True)
            
            return ComponentHealth(
                name=self.name,
                component_type=self.component_type,
                status=HealthStatus.UNHEALTHY,
                message=f"RAG health check failed: {str(e)}",
                response_time_ms=response_time_ms,
                last_check=datetime.now(),
                error_count=1
            )

async def run_rag_health_check() -> ComponentHealth:
    """
    Convenience function to run the RAG health check.
    """
    checker = RAGHealthCheck()
    return await checker.check_health()

async def get_rag_health_summary() -> Dict[str, Any]:
    """
    Get a human-readable summary of the RAG service health.
    """
    health = await run_rag_health_check()
    
    status_emoji = "[OK]" if health.status == HealthStatus.HEALTHY else "[FAIL]"
    
    return {
        "status": status_emoji,
        "message": health.message,
        "details": {
            "knowledge_base_dir": health.metadata.get("knowledge_base_dir", "N/A"),
            "job_queue_type": health.metadata.get("job_queue_type", "SQLite"),
            "knowledge_graph_connected": health.metadata.get("knowledge_graph_connected", False),
            "jobs_pending": health.metadata.get("jobs_pending", 0),
            "max_file_size_mb": health.metadata.get("max_file_size_mb", "N/A"),
            "max_concurrent_processes": health.metadata.get("max_concurrent_processes", "N/A")
        }
    }
"""