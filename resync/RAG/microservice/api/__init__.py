"""
RAG Microservice API Endpoints

This package contains the REST API endpoints for the RAG microservice.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from api.router import api_router

# Export the router
__all__ = ["api_router"]