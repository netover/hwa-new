from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from resync.core.container import app_container
from resync.core.interfaces import IAgentManager, IKnowledgeGraph, ITWSClient
from resync.main import app


@pytest.fixture
def mock_services():
    """Mocks core services in the DI container for testing the lifecycle."""
    # Create async mocks for our services
    mock_tws_client = AsyncMock(spec=ITWSClient)
    mock_kg_client = AsyncMock(spec=IKnowledgeGraph)
    mock_agent_manager = AsyncMock(spec=IAgentManager)

    # Use the container's 'register_instance' to override the real services
    # with our mocks for the duration of the test.
    with app_container.register_instance(ITWSClient, mock_tws_client), \
         app_container.register_instance(IKnowledgeGraph, mock_kg_client), \
         app_container.register_instance(IAgentManager, mock_agent_manager):
        yield {
            "tws_client": mock_tws_client,
            "kg_client": mock_kg_client,
            "agent_manager": mock_agent_manager,
        }


def test_lifespan_closes_clients_on_shutdown(mock_services):
    """
    Verifies that the application's lifespan manager correctly calls the
    close() method on TWS and KnowledgeGraph clients during shutdown.
    """
    # The TestClient context manager simulates the app startup and shutdown.
    with TestClient(app) as client:
        # Startup has run. We can make a dummy request to ensure the app is up.
        response = client.get("/docs")
        assert response.status_code == 200

    # When the 'with' block exits, shutdown events are triggered.
    mock_services["tws_client"].close.assert_called_once()
    mock_services["kg_client"].close.assert_called_once()
    mock_services["agent_manager"].load_agents_from_config.assert_called_once()
