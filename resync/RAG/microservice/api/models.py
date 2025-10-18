"""
RAG Microservice API Models

This module defines Pydantic models for the RAG microservice API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class UploadFileRequest(BaseModel):
    """Request model for file upload"""
    file_path: str = Field(..., description="Path to the file to be processed")
    original_filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(None, description="MIME type of the file")


class UploadFileResponse(BaseModel):
    """Response model for file upload"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Initial status ('queued')")
    message: str = Field(..., description="Status message")
    estimated_time: Optional[int] = Field(None, description="Estimated processing time in seconds")


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Current job status")
    progress: int = Field(..., description="Progress percentage (0-100)")
    message: str = Field(..., description="Current status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    chunks_created: Optional[int] = Field(None, description="Number of text chunks created")
    embeddings_generated: Optional[int] = Field(None, description="Number of embeddings generated")


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, description="Number of results to return", ge=1, le=50)
    threshold: Optional[float] = Field(0.7, description="Similarity threshold", ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional search filters")


class SearchResult(BaseModel):
    """Individual search result"""
    content: str = Field(..., description="Text content of the result")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Metadata about the source")
    chunk_id: str = Field(..., description="Unique identifier for this chunk")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results found")
    search_time: float = Field(..., description="Search execution time in seconds")


class HealthStatusResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall health status")
    message: str = Field(..., description="Health status message")
    details: Dict[str, Any] = Field(..., description="Detailed health information")
    timestamp: datetime = Field(..., description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")