from __future__ import annotations

import logging
from typing import Generator

from resync.core.agent_manager import agent_manager
from resync.services.tws_service import OptimizedTWSClient
from resync.services.mock_tws_service import MockTWSClient
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)


def get_tws_client() -> Generator[OptimizedTWSClient | MockTWSClient, None, None]:
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")
        
        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if not hasattr(agent_manager, "_mock_tws_client") or agent_manager._mock_tws_client is None:
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()
        
        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise
