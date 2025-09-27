"""
Tests for endpoints using dependency injection.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def test_websocket_endpoint_with_di(
    test_client: TestClient,
    mock_agent_manager: MagicMock,
    mock_connection_manager: MagicMock,
    mock_knowledge_graph: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the WebSocket endpoint with dependency injection."""
    # Setup mock agent
    agent_id = "test-agent"
    mock_agent = MagicMock()
    mock_agent.stream = AsyncMock()
    mock_agent.stream.return_value.__aiter__.return_value = ["Hello", " ", "World"]

    # Configure mock agent manager
    mock_agent_manager.get_agent.return_value = mock_agent

    # Use the TestClient for WebSocket testing
    with pytest.raises(WebSocketDisconnect):
        with test_client.websocket_connect(f"/ws/{agent_id}") as websocket:
            # Verify connection was accepted
            assert mock_connection_manager.connect.called

            # Send a message
            websocket.send_text("Test message")

            # Verify the response
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["sender"] == "user"
            assert response["message"] == "Test message"

            # Verify stream chunks
            for chunk in ["Hello", " ", "World"]:
                response = websocket.receive_json()
                assert response["type"] == "stream"
                assert response["sender"] == "agent"
                assert response["message"] == chunk

            # Verify final message
            response = websocket.receive_json()
            assert response["type"] == "message"
            assert response["sender"] == "agent"
            assert response["message"] == "Hello World"
            assert response["is_final"] is True

            # Verify knowledge graph was called
            assert mock_knowledge_graph.get_relevant_context.called
            assert mock_knowledge_graph.add_conversation.called

            # Close the connection
            websocket.close()
            assert mock_connection_manager.disconnect.called


def test_agent_not_found_with_di(
    test_client: TestClient,
    mock_agent_manager: MagicMock,
    mock_connection_manager: MagicMock,
):
    """Test WebSocket endpoint when agent is not found."""
    # Configure mock agent manager to return None
    mock_agent_manager.get_agent.return_value = None

    # Use the TestClient for WebSocket testing
    with pytest.raises(WebSocketDisconnect):
        with test_client.websocket_connect("/ws/nonexistent-agent") as websocket:
            # Verify connection was accepted but then closed
            assert mock_connection_manager.connect.called

            # Verify error message
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert "não encontrado" in response["message"]

            # Connection should be closed with code 1008
            # (Note: TestClient doesn't expose the close code)
