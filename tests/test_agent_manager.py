from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from resync.core.agent_manager import AgentManager


@pytest.fixture
def agent_manager_instance() -> AgentManager:
    """Provides a clean instance of the AgentManager for each test."""
    # Reset the singleton for isolation between tests
    AgentManager._instance = None
    AgentManager._initialized = False
    return AgentManager()


@pytest.fixture
def mock_config_file(tmp_path: Path) -> Path:
    """Creates a temporary agent configuration file for testing."""
    config_content = {
        "agents": [
            {
                "id": "test-agent-1",
                "name": "Test Agent 1",
                "role": "Testing",
                "goal": "To be tested",
                "backstory": "Born in a test",
                "tools": ["tws_status_tool"],
                "model_name": "test-model",
            }
        ]
    }
    config_file = tmp_path / "runtime.json"
    config_file.write_text(json.dumps(config_content))
    return config_file


def test_singleton_pattern(agent_manager_instance: AgentManager):
    """Ensures that the AgentManager follows the singleton pattern."""
    # The fixture already creates one instance
    instance1 = agent_manager_instance
    instance2 = AgentManager()
    assert instance1 is instance2


@patch("resync.core.agent_manager.OptimizedTWSClient")
def test_load_agents_from_config(
    mock_tws_client: MagicMock,
    agent_manager_instance: AgentManager,
    mock_config_file: Path,
):
    """
    Tests that agents are correctly loaded from a valid configuration file.
    """
    # Arrange
    # The agent_manager should use the mocked TWS client
    agent_manager_instance.tws_client = mock_tws_client

    # Act
    agent_manager_instance.load_agents_from_config(config_path=mock_config_file)

    # Assert
    assert "test-agent-1" in agent_manager_instance.agents
    agent = agent_manager_instance.get_agent("test-agent-1")
    assert agent is not None
    # Check if the system prompt was constructed correctly
    assert "You are Test Agent 1" in agent.system
    assert "tws_status_tool" in [t.name for t in agent.tools]


def test_load_agents_from_nonexistent_file(agent_manager_instance: AgentManager):
    """
    Tests that the agent manager handles a missing configuration file gracefully.
    """
    # Arrange
    non_existent_path = Path("non_existent_config.json")
    assert not non_existent_path.exists()

    # Act
    agent_manager_instance.load_agents_from_config(config_path=non_existent_path)

    # Assert
    assert agent_manager_instance.agents == {}


def test_load_agents_from_invalid_json(
    agent_manager_instance: AgentManager, tmp_path: Path
):
    """
    Tests that the agent manager handles a malformed JSON file gracefully.
    """
    # Arrange
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text("{'invalid': 'json',}")  # Malformed JSON

    # Act
    agent_manager_instance.load_agents_from_config(config_path=invalid_json_file)

    # Assert
    assert agent_manager_instance.agents == {}
