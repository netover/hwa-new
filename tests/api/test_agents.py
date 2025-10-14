from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from resync.core.agent_manager import AgentConfig
from resync.core.fastapi_di import get_agent_manager

# --- Sample Data for Mocking ---
sample_agent_config_1 = AgentConfig(
    id="test-agent-1",
    name="Test Agent 1",
    agent_type="chat",
    role="Tester",
    goal="To be tested",
    backstory="Born in a test",
    tools=["tws_status_tool"],
    model_name="test-model",
)

sample_agent_config_2 = AgentConfig(
    id="test-agent-2",
    name="Test Agent 2",
    agent_type="task",
    role="Another Tester",
    goal="To also be tested",
    backstory="Born in another test",
    tools=["tws_troubleshooting_tool"],
    model_name="test-model-2",
)


@pytest.fixture
def client(mock_agent_manager):
    """Create a TestClient for the FastAPI app."""
    from resync.api.agents import agents_router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(agents_router, prefix="/api/v1/agents")
    app.dependency_overrides[get_agent_manager] = lambda: mock_agent_manager
    return TestClient(app)


@pytest.fixture
def mock_agent_manager():
    """
    Fixture to provide a mock agent manager.
    """
    return AsyncMock()


def test_list_all_agents_success(client, mock_agent_manager):
    """
    Tests GET /api/v1/agents/ - successful retrieval of all agent configs.
    """
    # Arrange: Configure the mock to return a list of agent configs
    mock_agent_manager.get_all_agents.return_value = [
        sample_agent_config_1,
        sample_agent_config_2,
    ]

    # Act: Make a request to the endpoint
    response = client.get("/api/v1/agents/all")

    # Assert: Check the response
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["id"] == "test-agent-1"
    assert response_data[1]["id"] == "test-agent-2"


def test_get_agent_details_success(client, mock_agent_manager):
    """
    Tests GET /api/v1/agents/{agent_id} - successful retrieval of a single agent.
    """
    # Arrange: Configure the mock to return a specific agent config
    mock_agent_manager.get_agent_config.return_value = sample_agent_config_1

    # Act
    response = client.get("/api/v1/agents/test-agent-1")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == "test-agent-1"
    mock_agent_manager.get_agent_config.assert_called_once_with("test-agent-1")


def test_get_agent_details_not_found(client, mock_agent_manager):
    """
    Tests GET /api/v1/agents/{agent_id} - when the agent is not found.
    Should return 404 with standardized error response format.
    """
    # Arrange: Configure the mock to return None, simulating a not-found agent
    mock_agent_manager.get_agent_config.return_value = None

    # Act
    response = client.get("/api/v1/agents/non-existent-agent")

    # Assert: Should return 404 Not Found with proper error format
    assert response.status_code == 404
    response_data = response.json()

    # Assert the custom error response format
    assert "error_code" in response_data
    assert "message" in response_data
    assert "correlation_id" in response_data
    assert "timestamp" in response_data
    assert "severity" in response_data
    assert "category" in response_data

    # Check specific values for the NotFoundError
    assert response_data["error_code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in response_data["message"].lower()
    assert response_data["category"] == "BUSINESS_LOGIC"
    assert response_data["severity"] == "MEDIUM"
