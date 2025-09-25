import json
import logging
from pathlib import Path

import pytest

from resync.core.agent_manager import AgentConfig, AgentManager, AgentsConfig


@pytest.fixture
def agent_manager():
    """Fixture to provide a clean instance of AgentManager for each test."""
    # Reset the singleton for isolation between tests
    AgentManager._instance = None
    AgentManager._initialized = False
    return AgentManager()


@pytest.fixture
def test_agent_config():
    """Fixture to provide a deep copy of the test agent configuration for modification."""
    return {
        "id": "test_agent_1",
        "name": "Test Agent",
        "role": "Test Role",
        "goal": "Test Goal",
        "backstory": "Test Backstory",
        "tools": ["tws_status_tool"],
        "model_name": "llama3:latest",
        "memory": True,
        "verbose": False,
    }


def test_singleton_pattern():
    """Test that AgentManager follows singleton pattern."""
    manager1 = AgentManager()
    manager2 = AgentManager()
    assert manager1 is manager2


def test_init(agent_manager):
    """Test initialization of AgentManager."""
    assert isinstance(agent_manager.agents, dict)
    assert len(agent_manager.agents) == 0
    assert isinstance(agent_manager.agent_configs, list)
    assert len(agent_manager.agent_configs) == 0


def test_get_agent_non_existent(agent_manager):
    """Test retrieving a non-existent agent."""
    assert agent_manager.get_agent("non_existent_id") is None


def test_get_all_agents_empty(agent_manager):
    """Test getting all agents when none are loaded."""
    assert len(agent_manager.get_all_agents()) == 0


@pytest.mark.asyncio
async def test_load_agents_from_config_non_existent_file(agent_manager):
    """Test loading agents from a non-existent config file."""
    non_existent_path = Path("non_existent_config.json")
    await agent_manager.load_agents_from_config(non_existent_path)
    assert len(agent_manager.agents) == 0
    assert len(agent_manager.agent_configs) == 0


@pytest.mark.asyncio
async def test_load_agents_from_config_valid_file(
    agent_manager, test_agent_config, tmp_path
):
    """Test loading agents from a valid config file."""
    config_data = {"agents": [test_agent_config]}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    await agent_manager.load_agents_from_config(config_file)

    assert len(agent_manager.agents) == 1
    assert len(agent_manager.agent_configs) == 1
    assert "test_agent_1" in agent_manager.agents
    assert agent_manager.agent_configs[0].id == "test_agent_1"


def test_agent_config_model(test_agent_config):
    """Test the AgentConfig Pydantic model."""
    config = AgentConfig(**test_agent_config)
    assert config.id == "test_agent_1"
    assert config.name == "Test Agent"
    assert config.role == "Test Role"
    assert config.tools == ["tws_status_tool"]


def test_agents_config_model(test_agent_config):
    """Test the AgentsConfig Pydantic model."""
    config_data = {"agents": [test_agent_config]}
    config = AgentsConfig.parse_obj(config_data)
    assert len(config.agents) == 1
    assert config.agents[0].id == "test_agent_1"


def test_discover_tools(agent_manager):
    """Test the _discover_tools method."""
    tools = agent_manager._discover_tools()
    assert isinstance(tools, dict)
    assert "tws_status_tool" in tools
    assert "tws_troubleshooting_tool" in tools


@pytest.mark.asyncio
async def test_error_handling_missing_tool(
    agent_manager, caplog
):
    """Test error handling when getting agent with missing tool."""
    # Arrange: Load from default config
    await agent_manager.load_agents_from_config()

    # Act & Assert
    with pytest.raises(ValueError, match="not found"):
        agent_manager.get_agent_with_tool("test-agent-1", "non_existent_tool")
    
    # Check log
    assert "Tool 'non_existent_tool' not found for agent 'test-agent-1'" in caplog.text


@pytest.mark.asyncio
async def test_multiple_agents_loading(agent_manager, test_agent_config, tmp_path):
    """Test loading multiple agents from a config file."""
    test_agent_config2 = {
        "id": "test_agent_2",
        "name": "Test Agent 2",
        "role": "Test Role 2",
        "goal": "Test Goal 2",
        "backstory": "Test Backstory 2",
        "tools": ["tws_status_tool"],
        "model_name": "llama3:latest",
        "memory": True,
        "verbose": False,
    }
    config_data = {"agents": [test_agent_config, test_agent_config2]}
    config_file = tmp_path / "multi_agent_config.json"
    config_file.write_text(json.dumps(config_data))

    await agent_manager.load_agents_from_config(config_file)

    assert len(agent_manager.agents) == 2
    assert "test_agent_1" in agent_manager.agents
    assert "test_agent_2" in agent_manager.agents


@pytest.mark.asyncio
async def test_invalid_agent_id(agent_manager, tmp_path):
    """Test loading an agent with an invalid ID format."""
    invalid_config = {
        "id": "invalid_id",
        "name": "Test Agent",
        "role": "Test Role",
        "goal": "Test Goal",
        "backstory": "Test Backstory",
        "tools": ["tws_status_tool"],
        "model_name": "llama3:latest",
        "memory": True,
        "verbose": False,
    }
    config_data = {"agents": [invalid_config]}
    config_file = tmp_path / "invalid_id_config.json"
    config_file.write_text(json.dumps(config_data))

    await agent_manager.load_agents_from_config(config_file)

    assert "invalid_id" in agent_manager.agents
    # Add assertions based on expected validation behavior