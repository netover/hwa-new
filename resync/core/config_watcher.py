from __future__ import annotations

import logging
from typing import cast

from resync.core.di_container import container
from resync.core.interfaces import IAgentManager, IConnectionManager

logger = logging.getLogger(__name__)


async def handle_config_change() -> None:
    """
    Handles the reloading of agent configurations and notifies clients.
    """
    # Resolve dependencies from the DI container
    from resync.core.agent_manager import AgentManager
    from resync.core.connection_manager import ConnectionManager

    agent_manager = cast(AgentManager, container.get(IAgentManager))  # type: ignore[type-abstract]
    connection_manager = cast(ConnectionManager, container.get(IConnectionManager))  # type: ignore[type-abstract]

    logger.info("Configuration change detected. Reloading agents...")
    try:
        # Trigger the agent manager to reload its configuration
        await agent_manager.load_agents_from_config()
        logger.info("Agent configurations reloaded successfully.")

        # Get the updated list of agents
        agents = agent_manager.get_all_agents()
        agent_list = [{"id": agent.id, "name": agent.name} for agent in agents]

        # Notify all connected WebSocket clients about the change
        await connection_manager.broadcast_json(
            {
                "type": "config_update",
                "message": "A configuração do agente foi atualizada. A lista de agentes foi recarregada.",
                "agents": agent_list,
            }
        )
        logger.info("Broadcasted config update to all clients.")

    except Exception as e:
        logger.error("error_handling_config_change", error=str(e), exc_info=True)
