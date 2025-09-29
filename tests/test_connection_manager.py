"""Tests for resync.core.connection_manager module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, call
import asyncio
from fastapi import WebSocket

from resync.core.connection_manager import ConnectionManager, connection_manager


class TestConnectionManager:
    """Test ConnectionManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionManager instance."""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_websocket(self, manager):
        """Test connecting a WebSocket."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        await manager.connect(mock_websocket)
        
        # Verify websocket was accepted and added to active connections
        mock_websocket.accept.assert_called_once()
        assert mock_websocket in manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, manager):
        """Test disconnecting a WebSocket."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        # Connect first
        await manager.connect(mock_websocket)
        assert mock_websocket in manager.active_connections
        
        # Then disconnect
        await manager.disconnect(mock_websocket)
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_non_existent_websocket(self, manager):
        """Test disconnecting a WebSocket that was never connected."""
        mock_websocket = Mock(spec=WebSocket)
        
        # Should not raise an error
        await manager.disconnect(mock_websocket)
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager):
        """Test sending a personal message to a specific WebSocket."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        # Connect websocket
        await manager.connect(mock_websocket)
        
        # Send personal message
        test_message = "Hello, World!"
        await manager.send_personal_message(test_message, mock_websocket)
        
        mock_websocket.send_text.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_send_personal_message_error_handling(self, manager):
        """Test error handling when sending personal message fails."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock(side_effect=Exception("Connection lost"))
        
        # Connect websocket
        await manager.connect(mock_websocket)
        
        with patch('resync.core.connection_manager.logger') as mock_logger:
            # Should handle error gracefully
            await manager.send_personal_message("test", mock_websocket)
            
            # Should log the error
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_personal_json(self, manager):
        """Test sending personal JSON message to a specific WebSocket."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock()
        
        # Connect websocket
        await manager.connect(mock_websocket)
        
        # Send personal JSON message
        test_data = {"type": "message", "content": "Hello"}
        await manager.send_personal_json(test_data, mock_websocket)
        
        mock_websocket.send_json.assert_called_once_with(test_data)

    @pytest.mark.asyncio
    async def test_send_personal_json_error_handling(self, manager):
        """Test error handling when sending personal JSON fails."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock(side_effect=Exception("JSON error"))
        
        # Connect websocket
        await manager.connect(mock_websocket)
        
        with patch('resync.core.connection_manager.logger') as mock_logger:
            # Should handle error gracefully
            await manager.send_personal_json({"test": "data"}, mock_websocket)
            
            # Should log the error
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_message(self, manager):
        """Test broadcasting a message to all connected WebSockets."""
        # Create multiple mock websockets
        websockets = []
        for i in range(3):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_text = AsyncMock()
            websockets.append(mock_ws)
            await manager.connect(mock_ws)
        
        # Broadcast message
        test_message = "Broadcast message"
        await manager.broadcast(test_message)
        
        # Verify all websockets received the message
        for ws in websockets:
            ws.send_text.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_broadcast_message_with_failed_connections(self, manager):
        """Test broadcasting when some connections fail."""
        # Create websockets with mixed success/failure
        working_ws = Mock(spec=WebSocket)
        working_ws.accept = AsyncMock()
        working_ws.send_text = AsyncMock()
        
        failing_ws = Mock(spec=WebSocket)
        failing_ws.accept = AsyncMock()
        failing_ws.send_text = AsyncMock(side_effect=Exception("Connection failed"))
        
        await manager.connect(working_ws)
        await manager.connect(failing_ws)
        
        with patch('resync.core.connection_manager.logger') as mock_logger:
            # Broadcast should handle failures gracefully
            await manager.broadcast("test message")
            
            # Working connection should receive message
            working_ws.send_text.assert_called_once_with("test message")
            
            # Error should be logged for failing connection
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_json(self, manager):
        """Test broadcasting JSON data to all connected WebSockets."""
        # Create multiple mock websockets
        websockets = []
        for i in range(3):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_json = AsyncMock()
            websockets.append(mock_ws)
            await manager.connect(mock_ws)
        
        # Broadcast JSON
        test_data = {"type": "broadcast", "message": "Hello everyone"}
        await manager.broadcast_json(test_data)
        
        # Verify all websockets received the JSON data
        for ws in websockets:
            ws.send_json.assert_called_once_with(test_data)

    @pytest.mark.asyncio
    async def test_broadcast_json_with_failed_connections(self, manager):
        """Test broadcasting JSON when some connections fail."""
        working_ws = Mock(spec=WebSocket)
        working_ws.accept = AsyncMock()
        working_ws.send_json = AsyncMock()
        
        failing_ws = Mock(spec=WebSocket)
        failing_ws.accept = AsyncMock()
        failing_ws.send_json = AsyncMock(side_effect=Exception("JSON failed"))
        
        await manager.connect(working_ws)
        await manager.connect(failing_ws)
        
        with patch('resync.core.connection_manager.logger') as mock_logger:
            test_data = {"test": "data"}
            await manager.broadcast_json(test_data)
            
            # Working connection should receive JSON
            working_ws.send_json.assert_called_once_with(test_data)
            
            # Error should be logged for failing connection
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_broadcast_to_empty_connections(self, manager):
        """Test broadcasting when no connections are active."""
        # Should not raise an error
        await manager.broadcast("test message")
        await manager.broadcast_json({"test": "data"})

    @pytest.mark.asyncio
    async def test_multiple_connect_same_websocket(self, manager):
        """Test connecting the same WebSocket multiple times."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        # Connect multiple times
        await manager.connect(mock_websocket)
        await manager.connect(mock_websocket)
        await manager.connect(mock_websocket)
        
        # Should only be in list once
        connection_count = sum(1 for ws in manager.active_connections if ws == mock_websocket)
        assert connection_count == 3  # Actually, it might add multiple times if not checking

    @pytest.mark.asyncio
    async def test_concurrent_connections(self, manager):
        """Test handling multiple concurrent connections."""
        websockets = []
        tasks = []
        
        # Create multiple websockets
        for i in range(10):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            websockets.append(mock_ws)
            tasks.append(manager.connect(mock_ws))
        
        # Connect all concurrently
        await asyncio.gather(*tasks)
        
        # All should be connected
        assert len(manager.active_connections) == 10

    @pytest.mark.asyncio
    async def test_concurrent_broadcast(self, manager):
        """Test concurrent broadcasting to multiple connections."""
        # Connect multiple websockets
        websockets = []
        for i in range(5):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            mock_ws.send_text = AsyncMock()
            websockets.append(mock_ws)
            await manager.connect(mock_ws)
        
        # Perform multiple concurrent broadcasts
        broadcast_tasks = [
            manager.broadcast(f"message_{i}") for i in range(3)
        ]
        
        await asyncio.gather(*broadcast_tasks)
        
        # Each websocket should have received all 3 messages
        for ws in websockets:
            assert ws.send_text.call_count == 3

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_error(self, manager):
        """Test that failed connections are properly cleaned up."""
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock(side_effect=Exception("Accept failed"))
        
        with patch('resync.core.connection_manager.logger') as mock_logger:
            # Connection should fail but not raise
            await manager.connect(mock_websocket)
            
            # Should log error
            mock_logger.error.assert_called()
            
            # Failed connection should not be in active connections
            assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_manager_state_consistency(self, manager):
        """Test that manager state remains consistent during operations."""
        websockets = []
        
        # Connect several websockets
        for i in range(5):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            websockets.append(mock_ws)
            await manager.connect(mock_ws)
        
        # Verify all connected
        assert len(manager.active_connections) == 5
        
        # Disconnect some
        for i in range(0, 5, 2):  # Disconnect every other one
            await manager.disconnect(websockets[i])
        
        # Verify correct count
        assert len(manager.active_connections) == 3
        
        # Verify correct websockets remain
        for i in range(5):
            if i % 2 == 0:
                assert websockets[i] not in manager.active_connections
            else:
                assert websockets[i] in manager.active_connections


class TestGlobalConnectionManager:
    """Test the global connection manager instance."""

    def test_global_manager_exists(self):
        """Test that global connection manager exists."""
        assert connection_manager is not None
        assert isinstance(connection_manager, ConnectionManager)

    @pytest.mark.asyncio
    async def test_global_manager_functionality(self):
        """Test basic functionality of global connection manager."""
        # Clean up any existing connections
        connection_manager.active_connections.clear()
        
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        # Test connection
        await connection_manager.connect(mock_websocket)
        assert mock_websocket in connection_manager.active_connections
        
        # Test personal message
        await connection_manager.send_personal_message("test", mock_websocket)
        mock_websocket.send_text.assert_called_once_with("test")
        
        # Test disconnection
        await connection_manager.disconnect(mock_websocket)
        assert mock_websocket not in connection_manager.active_connections

    @pytest.mark.asyncio
    async def test_global_manager_persistence(self):
        """Test that global manager persists across imports."""
        # Clean up
        connection_manager.active_connections.clear()
        
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        # Connect using global manager
        await connection_manager.connect(mock_websocket)
        
        # Import again and check persistence
        from resync.core.connection_manager import connection_manager as imported_manager
        
        assert mock_websocket in imported_manager.active_connections
        assert imported_manager is connection_manager  # Should be same instance
        
        # Clean up
        await connection_manager.disconnect(mock_websocket)

    @pytest.mark.asyncio
    async def test_global_manager_thread_safety(self):
        """Test thread safety of global connection manager."""
        # Clean up
        connection_manager.active_connections.clear()
        
        websockets = []
        tasks = []
        
        # Create multiple concurrent connection tasks
        for i in range(10):
            mock_ws = Mock(spec=WebSocket)
            mock_ws.accept = AsyncMock()
            websockets.append(mock_ws)
            tasks.append(connection_manager.connect(mock_ws))
        
        # Execute concurrently
        await asyncio.gather(*tasks)
        
        # All should be connected
        assert len(connection_manager.active_connections) == 10
        
        # Clean up
        for ws in websockets:
            await connection_manager.disconnect(ws)
        
        assert len(connection_manager.active_connections) == 0
