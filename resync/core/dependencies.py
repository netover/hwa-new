from __future__ import annotations

import logging
from typing import Generator

from resync.core.agent_manager import agent_manager
from resync.services.tws_service import OptimizedTWSClient

# --- Logging Setup ---
logger = logging.getLogger(__name__)


def get_tws_client() -> Generator[OptimizedTWSClient, None, None]:
    """
    Dependency injector for the OptimizedTWSClient.

    This function provides a reliable way to get the singleton TWS client
    instance managed by the AgentManager. Using a generator-based dependency
    with `yield` ensures that resources can be properly managed if setup
    or teardown logic were needed.

    Yields:
        The singleton instance of the OptimizedTWSClient.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")
        # The agent_manager is responsible for lazily initializing the client
        client = agent_manager._get_tws_client()
        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(
            f"Failed to retrieve TWS client from AgentManager: {e}", exc_info=True
        )
        # In a real application, you might raise a specific HTTPException here
        # to prevent the endpoint from executing with a null client.
        # For now, we allow the error to propagate.
        raise
