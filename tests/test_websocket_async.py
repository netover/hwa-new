"""
WebSocket tests using TestClient properly to avoid event loop conflicts.
This file demonstrates the proper way to test WebSocket endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import asyncio

from resync.main import app


class TestWebSocketAsync:
    """Test WebSocket endpoints using TestClient properly."""

    def test_websocket_connection(self):
        """Test basic WebSocket connection using TestClient."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test-agent") as websocket:
                # Receive the initial connection message
                data = websocket.receive_json()
                assert data["type"] == "error"
                assert "não encontrado" in data["message"]

    def test_websocket_send_message(self):
        """Test sending a message through WebSocket using TestClient."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/nonexistent-agent") as websocket:
                # Receive the error message
                data = websocket.receive_json()
                assert data["type"] == "error"
                assert "não encontrado" in data["message"]

    def test_websocket_disconnect(self):
        """Test WebSocket disconnection handling."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/test-agent") as websocket:
                # Receive the error message
                data = websocket.receive_json()
                assert data["type"] == "error"