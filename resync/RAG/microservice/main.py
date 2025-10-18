"""
RAG Microservice Main Entry Point

This is the main FastAPI application for the standalone RAG microservice.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import our components
from api.router import api_router
from core.init_rag_service import init_rag_service
from config.settings import settings

# Create FastAPI app
app = FastAPI(
    title="RAG Microservice",
    description="Standalone service for Retrieval-Augmented Generation operations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, tags=["rag"])

# Initialize service on startup
@app.on_event("startup")
async def startup_event():
    await init_rag_service()

# Shutdown handler
@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)
