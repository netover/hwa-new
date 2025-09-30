from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import WebSocket, WebSocketDisconnect

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time updates.
    """

    def __init__(self) -> None:
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized.")

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection accepted: %s", websocket.client)
        logger.info("Total active connections: %d", len(self.active_connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket connection closed: %s", websocket.client)
            logger.info("Total active connections: %d", len(self.active_connections))

    async def broadcast(self, message: str) -> None:
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
            except (WebSocketDisconnect, ConnectionError) as e:
                # Client disconnected or connection lost during broadcast
                logger.warning("Connection issue during broadcast: %s", e)
            except RuntimeError as e: # pragma: no cover
                # WebSocket in wrong state
                if "websocket state" in str(e).lower():
                    logger.warning("WebSocket in wrong state during broadcast: %s", e)
                else:
                    logger.warning("Runtime error during broadcast: %s", e)
            except Exception:
                # Log error but don't stop broadcasting to other clients
                logger.error("Unexpected error during broadcast.", exc_info=True)

    async def broadcast_json(self, data: Dict[str, Any]) -> None:
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON broadcast requested, but no active connections.")
            return

        logger.info(
            "Broadcasting JSON data to %d clients.", len(self.active_connections)
        )
        tasks = [connection.send_json(data) for connection in self.active_connections]
        for task in tasks:
            try:
                await task
            except (WebSocketDisconnect, ConnectionError) as e:
                # Client disconnected or connection lost during broadcast
                logger.warning("Connection issue during JSON broadcast: %s", e)
            except RuntimeError as e: # pragma: no cover
                # WebSocket in wrong state
                if "websocket state" in str(e).lower():
                    logger.warning(
                        "WebSocket in wrong state during JSON broadcast: %s", e
                    )
                else:
                    logger.error("Runtime error during JSON broadcast: %s", e)
            except ValueError as e:
                # JSON serialization error
                logger.error("JSON serialization error during broadcast: %s", e, exc_info=True)
            except Exception:
                logger.error("Unexpected error during JSON broadcast.", exc_info=True)
