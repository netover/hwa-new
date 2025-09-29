"""Tests for resync.core.config_watcher module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from resync.core.config_watcher import handle_config_change


class TestConfigWatcher:
    """Test config watcher functionality."""

    @pytest.mark.asyncio
    async def test_handle_config_change_success(self):
        """Test successful config change handling."""
        # Mock agent manager
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        
        # Mock agent objects
        mock_agent_1 = Mock()
        mock_agent_1.id = "agent1"
        mock_agent_1.name = "Agent 1"
        
        mock_agent_2 = Mock()
        mock_agent_2.id = "agent2"  
        mock_agent_2.name = "Agent 2"
        
        mock_agent_manager.get_all_agents.return_value = [mock_agent_1, mock_agent_2]
        
        # Mock connection manager
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager):
            
            await handle_config_change()
            
            # Verify agent manager was called
            mock_agent_manager.load_agents_from_config.assert_called_once()
            mock_agent_manager.get_all_agents.assert_called_once()
            
            # Verify broadcast was called with correct data
            mock_connection_manager.broadcast_json.assert_called_once()
            broadcast_args = mock_connection_manager.broadcast_json.call_args[0][0]
            
            assert broadcast_args["type"] == "config_update"
            assert "A configuração do agente foi atualizada" in broadcast_args["message"]
            assert len(broadcast_args["agents"]) == 2
            assert broadcast_args["agents"][0]["id"] == "agent1"
            assert broadcast_args["agents"][0]["name"] == "Agent 1"
            assert broadcast_args["agents"][1]["id"] == "agent2"
            assert broadcast_args["agents"][1]["name"] == "Agent 2"

    @pytest.mark.asyncio
    async def test_handle_config_change_load_agents_error(self):
        """Test config change handling when loading agents fails."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock(
            side_effect=Exception("Failed to load agents")
        )
        
        mock_connection_manager = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager), \
             patch('resync.core.config_watcher.logger') as mock_logger:
            
            # Should not raise exception
            await handle_config_change()
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_args = mock_logger.error.call_args[0]
            assert "Error handling config change" in error_args[0]
            
            # Connection manager should not be called
            mock_connection_manager.broadcast_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_config_change_get_agents_error(self):
        """Test config change handling when getting agents fails."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        mock_agent_manager.get_all_agents.side_effect = Exception("Failed to get agents")
        
        mock_connection_manager = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager), \
             patch('resync.core.config_watcher.logger') as mock_logger:
            
            await handle_config_change()
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            
            # Connection manager should not be called
            mock_connection_manager.broadcast_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_config_change_broadcast_error(self):
        """Test config change handling when broadcast fails."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = []
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock(
            side_effect=Exception("Broadcast failed")
        )
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager), \
             patch('resync.core.config_watcher.logger') as mock_logger:
            
            await handle_config_change()
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            
            # Agent loading should still have been attempted
            mock_agent_manager.load_agents_from_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_config_change_empty_agents_list(self):
        """Test config change handling with empty agents list."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = []
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager):
            
            await handle_config_change()
            
            # Verify broadcast was called with empty agents list
            mock_connection_manager.broadcast_json.assert_called_once()
            broadcast_args = mock_connection_manager.broadcast_json.call_args[0][0]
            
            assert broadcast_args["type"] == "config_update"
            assert broadcast_args["agents"] == []

    @pytest.mark.asyncio
    async def test_handle_config_change_agents_with_none_values(self):
        """Test config change handling with agents having None values."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        
        # Mock agent with None name
        mock_agent_1 = Mock()
        mock_agent_1.id = "agent1"
        mock_agent_1.name = None
        
        # Mock agent with None id (edge case)
        mock_agent_2 = Mock()
        mock_agent_2.id = None
        mock_agent_2.name = "Agent 2"
        
        mock_agent_manager.get_all_agents.return_value = [mock_agent_1, mock_agent_2]
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager):
            
            await handle_config_change()
            
            # Verify broadcast was called and handled None values
            mock_connection_manager.broadcast_json.assert_called_once()
            broadcast_args = mock_connection_manager.broadcast_json.call_args[0][0]
            
            assert len(broadcast_args["agents"]) == 2
            assert broadcast_args["agents"][0]["id"] == "agent1"
            assert broadcast_args["agents"][0]["name"] is None
            assert broadcast_args["agents"][1]["id"] is None
            assert broadcast_args["agents"][1]["name"] == "Agent 2"

    @pytest.mark.asyncio
    async def test_handle_config_change_logging(self):
        """Test that appropriate logging occurs during config change."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = []
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager), \
             patch('resync.core.config_watcher.logger') as mock_logger:
            
            await handle_config_change()
            
            # Verify info logs were called
            assert mock_logger.info.call_count >= 3
            
            log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
            assert any("Configuration change detected" in log for log in log_calls)
            assert any("Agent configurations reloaded successfully" in log for log in log_calls)
            assert any("Broadcasted config update to all clients" in log for log in log_calls)

    @pytest.mark.asyncio
    async def test_handle_config_change_performance(self):
        """Test config change handling performance with many agents."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        
        # Create many mock agents
        agents = []
        for i in range(100):
            mock_agent = Mock()
            mock_agent.id = f"agent_{i}"
            mock_agent.name = f"Agent {i}"
            agents.append(mock_agent)
        
        mock_agent_manager.get_all_agents.return_value = agents
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager):
            
            start_time = asyncio.get_event_loop().time()
            await handle_config_change()
            end_time = asyncio.get_event_loop().time()
            
            # Should complete quickly even with many agents
            execution_time = end_time - start_time
            assert execution_time < 1.0  # Should take less than 1 second
            
            # Verify all agents were processed
            broadcast_args = mock_connection_manager.broadcast_json.call_args[0][0]
            assert len(broadcast_args["agents"]) == 100

    @pytest.mark.asyncio
    async def test_handle_config_change_concurrent_calls(self):
        """Test concurrent calls to handle_config_change."""
        mock_agent_manager = AsyncMock()
        mock_agent_manager.load_agents_from_config = AsyncMock()
        mock_agent_manager.get_all_agents.return_value = []
        
        mock_connection_manager = AsyncMock()
        mock_connection_manager.broadcast_json = AsyncMock()
        
        with patch('resync.core.config_watcher.agent_manager', mock_agent_manager), \
             patch('resync.core.config_watcher.connection_manager', mock_connection_manager):
            
            # Run multiple concurrent calls
            tasks = [handle_config_change() for _ in range(5)]
            await asyncio.gather(*tasks)
            
            # All calls should complete successfully
            assert mock_agent_manager.load_agents_from_config.call_count == 5
            assert mock_connection_manager.broadcast_json.call_count == 5

    @pytest.mark.asyncio
    async def test_handle_config_change_agent_manager_import_error(self):
        """Test handling of import error for agent_manager."""
        with patch('resync.core.config_watcher.agent_manager') as mock_agent_manager, \
             patch('resync.core.config_watcher.connection_manager') as mock_connection_manager, \
             patch('resync.core.config_watcher.logger') as mock_logger:
            
            # Configure mocks to raise import-like error
            mock_agent_manager.load_agents_from_config.side_effect = ImportError("Module not found")
            
            await handle_config_change()
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            
            # Connection manager should not be called
            mock_connection_manager.broadcast_json.assert_not_called()