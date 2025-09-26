from __future__ import annotations

import logging
from typing import List

from fastapi import WebSocket

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time updates.
    This class is a singleton to ensure a single list of active connections.
    """

    def __init__(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized.")

    async def connect(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection accepted: {websocket.client}")
        logger.info(f"Total active connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed: {websocket.client}")
            logger.info(f"Total active connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("Broadcast requested, but no active connections.")
            return

        logger.info(f"Broadcasting message to {len(self.active_connections)} clients.")
        # Create a list of tasks to send messages concurrently
        tasks = [
            connection.send_text(message) for connection in self.active_connections
        ]
        # In a high-load scenario, you might want to handle exceptions here
        # for failed sends, but for now, we keep it simple.
        for task in tasks:
            try:
                await task
            except Exception as e:
                # Log error but don't stop broadcasting to other clients
                logger.warning(f"Failed to send message to a client: {e}")

    async def broadcast_json(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON broadcast requested, but no active connections.")
            return

        logger.info(
            f"Broadcasting JSON data to {len(self.active_connections)} clients."
        )
        tasks = [connection.send_json(data) for connection in self.active_connections]
        for task in tasks:
            try:
                await task
            except Exception as e:
                logger.warning(f"Failed to send JSON to a client: {e}")


# --- Singleton Instance ---
# Create a single, globally accessible instance of the ConnectionManager.
connection_manager = ConnectionManager()
