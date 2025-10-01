from typing import List

from fastapi import APIRouter, Depends

from resync.core.agent_manager import AgentConfig
from resync.core.exceptions import NotFoundError
from resync.core.fastapi_di import get_agent_manager
from resync.core.interfaces import IAgentManager

agents_router = APIRouter()


@agents_router.get("/", response_model=List[AgentConfig])
async def list_all_agents(agent_manager: IAgentManager = Depends(get_agent_manager)):
    """
    Lists the configuration of all available agents.
    """
    return await agent_manager.get_all_agents()


@agents_router.get("/{agent_id}", response_model=AgentConfig)
async def get_agent_details(
    agent_id: str,
    agent_manager: IAgentManager = Depends(get_agent_manager),
):
    """
    Retrieves the detailed configuration of a specific agent by its ID.

    Raises:
        NotFoundError: If no agent with the specified ID is found.
    """
    agent_config = await agent_manager.get_agent_config(agent_id)
    if not agent_config:
        # Lança a exceção customizada. O manipulador de exceção do FastAPI
        # irá capturá-la e retornar um HTTP 404.
        raise NotFoundError(f"Agent with ID '{agent_id}' not found.")
    return agent_config