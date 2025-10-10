from typing import List

from fastapi import APIRouter, Depends, Request

from resync.core.agent_manager import AgentConfig
from resync.core.exceptions_enhanced import NotFoundError
from resync.core.fastapi_di import get_agent_manager
from resync.core.interfaces import IAgentManager
from resync.core.rate_limiter import critical_rate_limit
from resync.core.security import SafeAgentID

# Module-level dependency for agent manager to avoid B008 error
agent_manager_dependency = Depends(get_agent_manager)

agents_router = APIRouter()


@agents_router.get("/")
async def list_all_agents(request: Request):
    """
    Lists the configuration of all available agents.
    """
    # Return simple JSON response for now
    return [
        {
            "id": "tws-troubleshooting",
            "name": "TWS Troubleshooting Agent",
            "description": "Especialista em resolução de problemas do TWS",
            "model": "tongyi-deepresearch",
            "temperature": 0.7,
            "max_tokens": 4096
        },
        {
            "id": "tws-general",
            "name": "TWS General Assistant",
            "description": "Assistente geral para operações do TWS",
            "model": "openrouter-fallback",
            "temperature": 0.5,
            "max_tokens": 2048
        }
    ]


@agents_router.get("/{agent_id}")
async def get_agent_details(
    agent_id: SafeAgentID,
    request: Request,
):
    """
    Retrieves the detailed configuration of a specific agent by its ID.

    Raises:
        NotFoundError: If no agent with the specified ID is found.
    """
    # Return mock data for specific agent IDs
    agent_configs = {
        "tws-troubleshooting": {
            "id": "tws-troubleshooting",
            "name": "TWS Troubleshooting Agent",
            "description": "Especialista em resolução de problemas do TWS",
            "model": "tongyi-deepresearch",
            "temperature": 0.7,
            "max_tokens": 4096
        },
        "tws-general": {
            "id": "tws-general",
            "name": "TWS General Assistant",
            "description": "Assistente geral para operações do TWS",
            "model": "openrouter-fallback",
            "temperature": 0.5,
            "max_tokens": 2048
        }
    }

    if agent_id not in agent_configs:
        raise NotFoundError(f"Agent with ID '{agent_id}' not found.")

    return agent_configs[agent_id]
