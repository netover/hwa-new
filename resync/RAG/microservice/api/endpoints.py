from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.process_rag import process_rag_job, enqueue_rag_job, get_rag_job_status
from core.sqlite_job_queue import SQLiteJobQueue
from core.processor import RAGServiceProcessor
from config.settings import settings

# Global processor instance (would be better with dependency injection)
_rag_processor = None

router = APIRouter()

# Pydantic models for API responses
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None

class UploadResponse(BaseModel):
    job_id: str
    filename: str
    status: str

# Upload endpoint - accepts file and returns job_id immediately
class RAGUploadRequest(BaseModel):
    file: UploadFile = File(...)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for RAG processing.
    Returns immediately with a job_id.
    Processing happens asynchronously in the background.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get file size
    file.file.seek(0)  # Seek back to beginning
    
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB} MB"
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save file temporarily
    temp_path = Path(settings.RAG_KNOWLEDGE_BASE_DIR) / f"{job_id}_{file.filename}"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Enqueue job for processing
    await enqueue_rag_job(job_id, str(temp_path), file.filename)
    
    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        status="queued"
    )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status_endpoint(job_id: str):
    """
    Get the status of a RAG processing job.
    """
    status_info = await get_rag_job_status(job_id)

    return JobStatusResponse(
        job_id=job_id,
        status=status_info["status"],
        progress=status_info.get("progress"),
        message=status_info.get("message")
    )

@router.post("/search")
async def semantic_search(query: str, top_k: int = 5, threshold: Optional[float] = 0.7):
    """
    Perform semantic search over indexed documents.

    Args:
        query: Search query text
        top_k: Number of results to return (max 50)
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        Search results with content, scores, and metadata
    """
    global _rag_processor

    # Initialize processor if not done
    if _rag_processor is None:
        try:
            _rag_processor = RAGServiceProcessor()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize RAG processor: {str(e)}"
            )

    # Validate parameters
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")

    if threshold is not None and (threshold < 0.0 or threshold > 1.0):
        raise HTTPException(status_code=400, detail="threshold must be between 0.0 and 1.0")

    try:
        # Perform search
        results = await _rag_processor.search_similar(query, top_k=top_k)

        # Apply threshold filter if specified
        if threshold is not None:
            results = [r for r in results if r.get('score', 0) >= threshold]

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "threshold_applied": threshold is not None
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the RAG microservice.

    Returns comprehensive health status including:
    - Service availability
    - Vector store status
    - Job queue status
    - Processing statistics
    """
    global _rag_processor

    health_info = {
        "service": "rag-microservice",
        "status": "healthy",
        "timestamp": str(uuid.uuid4()),  # Simple timestamp replacement
        "components": {}
    }

    try:
        # Check vector store
        if _rag_processor and hasattr(_rag_processor, 'get_processing_stats'):
            stats = await _rag_processor.get_processing_stats()
            health_info["components"]["vector_store"] = {
                "status": "healthy",
                "type": stats.get("vector_store_type", "unknown"),
                "documents": stats.get("vector_store_stats", {}).get("total_documents", 0)
            }
        else:
            health_info["components"]["vector_store"] = {
                "status": "uninitialized",
                "type": "unknown",
                "documents": 0
            }

        # Check job queue
        try:
            job_queue = SQLiteJobQueue()
            pending_count = await job_queue.get_pending_jobs_count()
            health_info["components"]["job_queue"] = {
                "status": "healthy",
                "pending_jobs": pending_count,
                "type": "sqlite"
            }
        except Exception as e:
            health_info["components"]["job_queue"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check file system
        knowledge_base_path = Path(settings.RAG_KNOWLEDGE_BASE_DIR)
        health_info["components"]["filesystem"] = {
            "status": "healthy" if knowledge_base_path.exists() else "unhealthy",
            "knowledge_base_path": str(knowledge_base_path),
            "accessible": os.access(knowledge_base_path, os.R_OK)
        }

        # Determine overall status
        component_statuses = [comp.get("status", "unknown") for comp in health_info["components"].values()]
        if "unhealthy" in component_statuses:
            health_info["status"] = "degraded"
        elif "uninitialized" in component_statuses:
            health_info["status"] = "initializing"

        return health_info

    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        return health_info

# Export the router
rag_router = router