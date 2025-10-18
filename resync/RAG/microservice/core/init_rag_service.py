"""
RAG Microservice Initialization

This module initializes the RAG microservice components on startup.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.process_rag import init_rag_processing
from core.file_ingestor import FileIngestor, create_file_ingestor
from core.knowledge_graph_circuit_breaker import CircuitBreakerAsyncKnowledgeGraph
from core.sqlite_job_queue import SQLiteJobQueue
from config.settings import settings

# Global variables
_knowledge_graph: Optional[CircuitBreakerAsyncKnowledgeGraph] = None
_file_ingestor: Optional[FileIngestor] = None
_rag_job_queue: Optional[SQLiteJobQueue] = None

async def init_rag_service() -> None:
    """
    Initialize the RAG microservice on startup.
    This includes:
    - Loading existing documents from knowledge base
    - Initializing components
    - Setting up any required connections
    - Starting the job processing loop
    """
    global _knowledge_graph, _file_ingestor, _rag_job_queue

    try:
        # Initialize SQLite job queue (no connection needed)
        _rag_job_queue = SQLiteJobQueue()

        # Initialize knowledge graph with circuit breaker
        _knowledge_graph = CircuitBreakerAsyncKnowledgeGraph()

        # Initialize file ingestor
        _file_ingestor = create_file_ingestor()

        # Load existing documents from knowledge base
        # This is important for CPU-only systems to avoid reprocessing
        knowledge_base_dir = Path(settings.RAG_KNOWLEDGE_BASE_DIR)

        if knowledge_base_dir.exists():
            logger.info(f"Loading existing documents from {knowledge_base_dir}")
            # In a real implementation, this would load from the knowledge graph
            # For now, we'll just log
            for file_path in knowledge_base_dir.rglob("*"):
                if file_path.is_file():
                    logger.info(f"Found existing document: {file_path.name}")

        # Start the RAG job processing loop
        await init_rag_processing()

        logger.info("RAG microservice initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize RAG microservice: {str(e)}", exc_info=True)
        raise

async def get_rag_components() -> Dict[str, Any]:
    """
    Get the initialized RAG components.
    This is useful for testing and debugging.
    """
    return {
        "knowledge_graph": _knowledge_graph,
        "file_ingestor": _file_ingestor,
        "job_queue": _rag_job_queue
    }

# Initialize logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)