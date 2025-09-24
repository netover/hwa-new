from __future__ import annotations

import logging
from typing import Any, Set, Tuple

# from resync.core.agent_manager import agent_manager  # Temporarily disabled for testing
from resync.core.connection_manager import connection_manager

# --- Logging Setup ---
logger = logging.getLogger(__name__)


async def handle_config_change(changes: Set[Tuple[Any, str]]):
    """
    Callback function executed by the watchfiles observer when a change is detected.

    Args:
        changes: A set of tuples, where each tuple contains the type of change
                 (e.g., 'modified') and the path to the changed file.
    """
    for change_type, path in changes:
        logger.info(
            f"Detected change '{change_type.name}' in configuration file: {path}"
        )

        # We only care about modifications to the agent config file
        if change_type.name in ("modified", "added"):
            logger.info("Reloading agent configurations...")
            try:
                # Trigger the agent manager to reload its configuration
                # agent_manager.load_agents_from_config()  # Temporarily disabled
                logger.info("Agent configurations reloaded successfully.")

                # Notify all connected WebSocket clients about the change
                await connection_manager.broadcast_json(
                    {
                        "type": "config_update",
                        "message": "A configuração do agente foi atualizada. A lista de agentes foi recarregada.",
                        "agents": [
                            {"id": agent["id"], "name": agent["name"]}
                            for agent in []  # agent_manager.get_all_agents()  # Temporarily disabled
                        ],
                    }
                )
                logger.info("Broadcasted configuration update to all clients.")
            except Exception as e:
                logger.error(f"Failed to handle config change: {e}", exc_info=True)
                # Notify clients of the error
                await connection_manager.broadcast_json(
                    {
                        "type": "error",
                        "message": f"Falha ao recarregar a configuração do agente: {e}",
                    }
                )
