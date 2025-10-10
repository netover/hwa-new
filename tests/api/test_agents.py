from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from resync.core.agent_manager import AgentConfig
from resync.core.fastapi_di import get_agent_manager
from resync.main import app

# Use the TestClient with our main FastAPI app
# Patch the rate limit decorator to skip rate limiting during tests
def mock_rate_limit_decorator(func):
    return func

with patch('resync.lifespan.initialize_redis_with_retry'), \
     patch('resync.core.rate_limiter.critical_rate_limit', mock_rate_limit_decorator):
    client = TestClient(app)

# --- Sample Data for Mocking ---
sample_agent_config_1 = AgentConfig(
    id="test-agent-1",
    name="Test Agent 1",
    role="Tester",
    goal="To be tested",
    backstory="Born in a test",
    tools=["tws_status_tool"],
    model_name="test-model",
)

sample_agent_config_2 = AgentConfig(
    id="test-agent-2",
    name="Test Agent 2",
    role="Another Tester",
    goal="To also be tested",
    backstory="Born in another test",
    tools=["tws_troubleshooting_tool"],
    model_name="test-model-2",
)


@pytest.fixture
def mock_agent_manager():
    """
    Fixture to provide a mock agent manager and override the FastAPI dependency
    for the duration of a test.
    """
    mock_manager = AsyncMock()
    # Override the dependency injection for get_agent_manager
    app.dependency_overrides[get_agent_manager] = lambda: mock_manager
    yield mock_manager
    # Clean up the override after the test is done
    del app.dependency_overrides[get_agent_manager]


def test_list_all_agents_success(mock_agent_manager):
    """
    Tests GET /api/v1/agents/ - successful retrieval of all agent configs.
    """
    # Arrange: Configure the mock to return a list of agent configs
    mock_agent_manager.get_all_agents.return_value = [
        sample_agent_config_1,
        sample_agent_config_2,
    ]

    # Act: Make a request to the endpoint
    response = client.get("/api/v1/agents/")

    # Assert: Check the response
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["id"] == "test-agent-1"
    assert response_data[1]["id"] == "test-agent-2"


def test_get_agent_details_success(mock_agent_manager):
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


def test_get_agent_details_not_found(mock_agent_manager):
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

    # Assert the RFC 7807 Problem Details format with custom extensions
    assert "type" in response_data
    assert "title" in response_data
    assert "status" in response_data
    assert "detail" in response_data
    assert "instance" in response_data
    assert "correlation_id" in response_data
    assert "timestamp" in response_data
    assert "error_code" in response_data
    assert "severity" in response_data

    # Check specific values for the NotFoundError
    assert response_data["status"] == 404
    assert response_data["error_code"] == "RESOURCE_NOT_FOUND"
    assert "Resource Not Found" in response_data["title"]
    assert "Not Found" in response_data["detail"]
    assert response_data["instance"] == "/api/v1/agents/non-existent-agent"
    assert response_data["severity"] == "info"
