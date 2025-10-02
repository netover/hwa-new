"""
Manages the application's lifespan events (startup and shutdown).

This module is responsible for initializing and closing resources such as
database connections, background tasks, and service clients.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from resync.core.di_container import container
from resync.core.interfaces import IAgentManager, IKnowledgeGraph, ITWSClient

logger = logging.getLogger(__name__)


async def validate_runtime_config() -> dict:
    """
    Validates the runtime configuration and returns validation results.
    
    Returns:
        dict: Validation results with status and any issues found
    """
    try:
        # Check if all required services are properly configured
        validation_results = {
            "status": "valid",
            "issues": [],
            "services": {}
        }
        
        # Validate agent manager
        try:
            agent_manager = container.get(IAgentManager)
            validation_results["services"]["agent_manager"] = "configured"
        except Exception as e:
            validation_results["services"]["agent_manager"] = f"error: {str(e)}"
            validation_results["issues"].append(f"Agent manager configuration error: {str(e)}")
        
        # Validate TWS client
        try:
            tws_client = container.get(ITWSClient)
            validation_results["services"]["tws_client"] = "configured"
        except Exception as e:
            validation_results["services"]["tws_client"] = f"error: {str(e)}"
            validation_results["issues"].append(f"TWS client configuration error: {str(e)}")
        
        # Validate knowledge graph
        try:
            kg = container.get(IKnowledgeGraph)
            validation_results["services"]["knowledge_graph"] = "configured"
        except Exception as e:
            validation_results["services"]["knowledge_graph"] = f"error: {str(e)}"
            validation_results["issues"].append(f"Knowledge graph configuration error: {str(e)}")
        
        # Update overall status based on issues
        if validation_results["issues"]:
            validation_results["status"] = "invalid"
        else:
            validation_results["status"] = "valid"
            
        return validation_results
        
    except Exception as e:
        logger.error(f"Runtime configuration validation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "issues": [f"Validation system error: {str(e)}"],
            "services": {}
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    """
    # --- Startup ---
    logger.info("Application startup: Initializing services...")
    agent_manager = container.get(IAgentManager)
    await agent_manager.load_agents_from_config()
    logger.info("Application startup complete.")

    yield

    # --- Shutdown ---
    logger.info("Application shutdown: Closing resources...")
    tws_client = container.get(ITWSClient)
    await tws_client.close()
    knowledge_graph = container.get(IKnowledgeGraph)
    await knowledge_graph.close()
    logger.info("Application shutdown complete.")