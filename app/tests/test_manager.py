import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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


@pytest.mark.asyncio
async def test_tws_monitor_agent_triggers_rag_on_abend(
    manager: AgentManager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests the full RAG integration flow for the TWS_Monitor agent.
    """
    # 1. Setup Mocks
    mock_tws_run = AsyncMock(
        return_value={
            "jobs_found": 1,
            "jobs": [{"name": "CRITICAL_JOB", "status": "ABEND"}],
        }
    )
    monkeypatch.setattr("app.tools.tws_tool_readonly.TWSToolReadOnly.run", mock_tws_run)

    mock_kb_search = MagicMock(
        return_value={"solution": "Restart the database service."}
    )
    monkeypatch.setattr(
        "app.services.knowledge_service.KnowledgeBaseService.search_for_solution",
        mock_kb_search,
    )

    # 2. Load the agent configuration
    # This config enables the TWS_Monitor
    config = {
        "agents": {
            "TWS_Monitor": {"enabled": True, "tools": ["tws_readonly"]},
        }
    }
    await manager.initialize_tools()
    await manager.reload_agents_from_file(config)

    # 3. Get the enhanced agent and run it
    tws_agent = manager.agents.get("TWS_Monitor")
    assert tws_agent is not None

    result = await tws_agent.run("get_job_status", name="CRITICAL_JOB")

    # 4. Assertions
    # Ensure the TWS tool was called
    mock_tws_run.assert_awaited_once_with("get_job_status", name="CRITICAL_JOB")

    # Ensure the knowledge base was searched because the job was in ABEND
    mock_kb_search.assert_called_once_with("CRITICAL_JOB")

    # Ensure the final result is augmented with the RAG info
    assert "knowledge_base_info" in result
    assert result["knowledge_base_info"]["solution"] == "Restart the database service."
