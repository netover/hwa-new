"""
Dependency Injection Tests

This module tests the dependency injection patterns implemented in the application,
ensuring proper AgentManager instance management and dependency resolution.
"""

from unittest.mock import MagicMock, patch

import pytest

from resync.core.agent_manager import AgentManager
from resync.core.dependencies import get_tws_client


class TestDependencyInjection:
    """Test dependency injection patterns."""

    @pytest.mark.di
    def test_tws_client_dependency_injection(self, mock_agent_manager):
        """Test TWS client dependency injection."""
        with patch(
            "resync.core.dependencies.agent_manager"
        ) as mock_agent_manager_module:
            mock_agent_manager_module._get_tws_client.return_value = MagicMock()

            # Test that we can get TWS client
            gen = get_tws_client()
            client = next(gen)
            assert client is not None

    @pytest.mark.di
    def test_tws_client_mock_mode(self):
        """Test TWS client in mock mode."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                mock_settings.TWS_MOCK_MODE = True
                mock_agent_manager._mock_tws_client = MagicMock()

                # Test that mock client is returned when TWS_MOCK_MODE is True
                gen = get_tws_client()
                client = next(gen)
                assert client is not None

    @pytest.mark.di
    def test_dependency_error_handling(self):
        """Test error handling in dependency injection."""
        with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
            # Simulate agent manager failure
            mock_agent_manager._get_tws_client.side_effect = Exception(
                "TWS client unavailable"
            )

            gen = get_tws_client()
            with pytest.raises(Exception, match="TWS client unavailable"):
                next(gen)

    @pytest.mark.di
    def test_dependency_caching(self):
        """Test that dependencies are properly cached."""
        call_count = 0

        def mock_tws_factory():
            nonlocal call_count
            call_count += 1
            return MagicMock()

        with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
            mock_agent_manager._get_tws_client.side_effect = mock_tws_factory

            # First call should create new instance
            gen1 = get_tws_client()
            client1 = next(gen1)
            assert call_count == 1

            # Second call should reuse cached instance
            gen2 = get_tws_client()
            client2 = next(gen2)
            assert call_count == 1  # Should still be 1, not 2

    @pytest.mark.di
    def test_environment_specific_dependencies(self):
        """Test environment-specific dependency configuration."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                # Test with mock mode enabled
                mock_settings.TWS_MOCK_MODE = True
                mock_agent_manager._mock_tws_client = MagicMock()

                client = next(get_tws_client())
                assert client is not None


class TestAgentManager:
    """Test AgentManager functionality."""

    @pytest.mark.di
    def test_agent_manager_initialization(self):
        """Test AgentManager initialization."""
        with patch.object(AgentManager, "load_agents_from_config", return_value=[]):
            manager = AgentManager()
            assert manager is not None
            assert manager.agents == {}
            assert manager.agent_configs == []

    @pytest.mark.di
    def test_agent_manager_singleton_behavior(self):
        """Test that AgentManager behaves as singleton."""
        manager1 = AgentManager()
        manager2 = AgentManager()
        assert manager1 is manager2

    @pytest.mark.di
    def test_agent_manager_get_agent(self):
        """Test AgentManager get_agent method."""
        manager = AgentManager()
        agent = manager.get_agent("nonexistent")
        assert agent is None

    @pytest.mark.di
    def test_agent_manager_get_all_agents(self):
        """Test AgentManager get_all_agents method."""
        with patch.object(AgentManager, "load_agents_from_config", return_value=[]):
            manager = AgentManager()
            agents = manager.get_all_agents()
            assert agents == []

    @pytest.mark.di
    def test_agent_manager_tools_discovery(self):
        """Test AgentManager tools discovery."""
        manager = AgentManager()
        tools = manager._discover_tools()
        assert isinstance(tools, dict)
        assert "tws_status_tool" in tools
        assert "tws_troubleshooting_tool" in tools
