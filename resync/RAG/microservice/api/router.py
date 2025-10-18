from fastapi import APIRouter
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.endpoints import rag_router

api_router = APIRouter()
api_router.include_router(rag_router, tags=["rag"])

# Export the router
__all__ = ["api_router"]