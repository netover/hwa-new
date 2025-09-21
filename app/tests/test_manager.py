import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.manager import AgentManager


@pytest.fixture
def manager() -> AgentManager:
    """Provides a fresh AgentManager instance for each test."""
    return AgentManager()


@pytest.fixture
def mock_config_file(tmp_path: Path) -> Path:
    """Creates a temporary runtime.json file for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "runtime.json"
    config_data = {
        "default_model": "mock_model",
        "agents": {
            "TWS_Monitor": {
                "enabled": True,
                "provider": "openrouter",
                "tools": ["tws_readonly"],
                "role": "Test TWS Monitor",
            }
        },
    }
    config_file.write_text(json.dumps(config_data))
    return config_file


@pytest.mark.asyncio
async def test_manager_initialize_loads_agents(
    manager: AgentManager, mock_config_file: Path, monkeypatch
) -> None:
    """
    Tests if the manager's initialize method correctly loads agents
    from the configuration file.
    """
    # Mock the watcher so it doesn't run in the background during tests
    monkeypatch.setattr("app.agents.manager.watch_config_and_reload", AsyncMock())

    # Mock the Path methods to simulate reading our temp config file
    # without actually changing the Path object itself.
    mock_content = mock_config_file.read_text()
    monkeypatch.setattr("pathlib.Path.is_file", lambda self: True)
    monkeypatch.setattr("pathlib.Path.read_text", lambda self: mock_content)

    await manager.initialize()

    # Check that the dispatcher and the configured agent are loaded
    assert "dispatcher" in manager.agents
    assert "TWS_Monitor" in manager.agents
    assert manager.agents["TWS_Monitor"].role == "Test TWS Monitor"

    # Check that the dispatcher property works
    assert manager.dispatcher is not None
    assert manager.dispatcher.name == "Dispatcher"


@pytest.mark.asyncio
async def test_manager_reload_agents_from_dict(manager: AgentManager) -> None:
    """
    Tests if the manager can reload its agent configuration from a dictionary.
    """
    new_config = {
        "default_model": "reloaded_model",
        "agents": {
            "New_Agent": {
                "enabled": True,
                "provider": "openrouter",
                "role": "A newly reloaded agent",
            }
        },
    }

    # Manually initialize tools as initialize() would do
    await manager.initialize_tools()

    await manager.reload_agents_from_file(new_config)

    assert "dispatcher" in manager.agents
    assert "New_Agent" in manager.agents
    assert "TWS_Monitor" not in manager.agents  # Old agent should be gone
    assert manager.agents["New_Agent"].role == "A newly reloaded agent"
    assert manager.dispatcher is not None
    assert manager.dispatcher.model.id == "reloaded_model"
