from __future__ import annotations

import logging

from resync.core.connection_manager import connection_manager

logger = logging.getLogger(__name__)


async def handle_config_change() -> None:
    """
    Handles the reloading of agent configurations and notifies clients.
    """
    from resync.core.agent_manager import agent_manager

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
        logger.error(f"Error handling config change: {e}", exc_info=True)
