from __future__ import annotations

import logging
from typing import List

from fastapi import WebSocket

# --- Logging Setup ---
logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class ConnectionManager:
    """
    Manages active WebSocket connections for real-time updates.
    This class is a singleton to ensure a single list of active connections.
    """

    def xǁConnectionManagerǁ__init____mutmut_orig(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized.")

    def xǁConnectionManagerǁ__init____mutmut_1(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = None
        logger.info("ConnectionManager initialized.")

    def xǁConnectionManagerǁ__init____mutmut_2(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info(None)

    def xǁConnectionManagerǁ__init____mutmut_3(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("XXConnectionManager initialized.XX")

    def xǁConnectionManagerǁ__init____mutmut_4(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("connectionmanager initialized.")

    def xǁConnectionManagerǁ__init____mutmut_5(self):
        """Initializes the ConnectionManager with an empty list of connections."""
        self.active_connections: List[WebSocket] = []
        logger.info("CONNECTIONMANAGER INITIALIZED.")

    xǁConnectionManagerǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁConnectionManagerǁ__init____mutmut_1": xǁConnectionManagerǁ__init____mutmut_1,
        "xǁConnectionManagerǁ__init____mutmut_2": xǁConnectionManagerǁ__init____mutmut_2,
        "xǁConnectionManagerǁ__init____mutmut_3": xǁConnectionManagerǁ__init____mutmut_3,
        "xǁConnectionManagerǁ__init____mutmut_4": xǁConnectionManagerǁ__init____mutmut_4,
        "xǁConnectionManagerǁ__init____mutmut_5": xǁConnectionManagerǁ__init____mutmut_5,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁConnectionManagerǁ__init____mutmut_orig"),
            object.__getattribute__(
                self, "xǁConnectionManagerǁ__init____mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(
        xǁConnectionManagerǁ__init____mutmut_orig
    )
    xǁConnectionManagerǁ__init____mutmut_orig.__name__ = "xǁConnectionManagerǁ__init__"

    async def xǁConnectionManagerǁconnect__mutmut_orig(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection accepted: {websocket.client}")
        logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁconnect__mutmut_1(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(None)
        logger.info(f"New WebSocket connection accepted: {websocket.client}")
        logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁconnect__mutmut_2(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(None)
        logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁconnect__mutmut_3(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection accepted: {websocket.client}")
        logger.info(None)

    xǁConnectionManagerǁconnect__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁConnectionManagerǁconnect__mutmut_1": xǁConnectionManagerǁconnect__mutmut_1,
        "xǁConnectionManagerǁconnect__mutmut_2": xǁConnectionManagerǁconnect__mutmut_2,
        "xǁConnectionManagerǁconnect__mutmut_3": xǁConnectionManagerǁconnect__mutmut_3,
    }

    def connect(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁConnectionManagerǁconnect__mutmut_orig"),
            object.__getattribute__(
                self, "xǁConnectionManagerǁconnect__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    connect.__signature__ = _mutmut_signature(xǁConnectionManagerǁconnect__mutmut_orig)
    xǁConnectionManagerǁconnect__mutmut_orig.__name__ = "xǁConnectionManagerǁconnect"

    async def xǁConnectionManagerǁdisconnect__mutmut_orig(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed: {websocket.client}")
            logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁdisconnect__mutmut_1(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket not in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed: {websocket.client}")
            logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁdisconnect__mutmut_2(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(None)
            logger.info(f"WebSocket connection closed: {websocket.client}")
            logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁdisconnect__mutmut_3(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(None)
            logger.info(f"Total active connections: {len(self.active_connections)}")

    async def xǁConnectionManagerǁdisconnect__mutmut_4(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active list.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed: {websocket.client}")
            logger.info(None)

    xǁConnectionManagerǁdisconnect__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁConnectionManagerǁdisconnect__mutmut_1": xǁConnectionManagerǁdisconnect__mutmut_1,
        "xǁConnectionManagerǁdisconnect__mutmut_2": xǁConnectionManagerǁdisconnect__mutmut_2,
        "xǁConnectionManagerǁdisconnect__mutmut_3": xǁConnectionManagerǁdisconnect__mutmut_3,
        "xǁConnectionManagerǁdisconnect__mutmut_4": xǁConnectionManagerǁdisconnect__mutmut_4,
    }

    def disconnect(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁConnectionManagerǁdisconnect__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁConnectionManagerǁdisconnect__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    disconnect.__signature__ = _mutmut_signature(
        xǁConnectionManagerǁdisconnect__mutmut_orig
    )
    xǁConnectionManagerǁdisconnect__mutmut_orig.__name__ = (
        "xǁConnectionManagerǁdisconnect"
    )

    async def xǁConnectionManagerǁbroadcast__mutmut_orig(self, message: str):
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

    async def xǁConnectionManagerǁbroadcast__mutmut_1(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if self.active_connections:
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

    async def xǁConnectionManagerǁbroadcast__mutmut_2(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info(None)
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

    async def xǁConnectionManagerǁbroadcast__mutmut_3(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("XXBroadcast requested, but no active connections.XX")
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

    async def xǁConnectionManagerǁbroadcast__mutmut_4(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("broadcast requested, but no active connections.")
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

    async def xǁConnectionManagerǁbroadcast__mutmut_5(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("BROADCAST REQUESTED, BUT NO ACTIVE CONNECTIONS.")
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

    async def xǁConnectionManagerǁbroadcast__mutmut_6(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("Broadcast requested, but no active connections.")
            return

        logger.info(None)
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

    async def xǁConnectionManagerǁbroadcast__mutmut_7(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("Broadcast requested, but no active connections.")
            return

        logger.info(f"Broadcasting message to {len(self.active_connections)} clients.")
        # Create a list of tasks to send messages concurrently
        tasks = None
        # In a high-load scenario, you might want to handle exceptions here
        # for failed sends, but for now, we keep it simple.
        for task in tasks:
            try:
                await task
            except Exception as e:
                # Log error but don't stop broadcasting to other clients
                logger.warning(f"Failed to send message to a client: {e}")

    async def xǁConnectionManagerǁbroadcast__mutmut_8(self, message: str):
        """
        Sends a plain text message to all connected clients.
        """
        if not self.active_connections:
            logger.info("Broadcast requested, but no active connections.")
            return

        logger.info(f"Broadcasting message to {len(self.active_connections)} clients.")
        # Create a list of tasks to send messages concurrently
        tasks = [connection.send_text(None) for connection in self.active_connections]
        # In a high-load scenario, you might want to handle exceptions here
        # for failed sends, but for now, we keep it simple.
        for task in tasks:
            try:
                await task
            except Exception as e:
                # Log error but don't stop broadcasting to other clients
                logger.warning(f"Failed to send message to a client: {e}")

    async def xǁConnectionManagerǁbroadcast__mutmut_9(self, message: str):
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
            except Exception:
                # Log error but don't stop broadcasting to other clients
                logger.warning(None)

    xǁConnectionManagerǁbroadcast__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁConnectionManagerǁbroadcast__mutmut_1": xǁConnectionManagerǁbroadcast__mutmut_1,
        "xǁConnectionManagerǁbroadcast__mutmut_2": xǁConnectionManagerǁbroadcast__mutmut_2,
        "xǁConnectionManagerǁbroadcast__mutmut_3": xǁConnectionManagerǁbroadcast__mutmut_3,
        "xǁConnectionManagerǁbroadcast__mutmut_4": xǁConnectionManagerǁbroadcast__mutmut_4,
        "xǁConnectionManagerǁbroadcast__mutmut_5": xǁConnectionManagerǁbroadcast__mutmut_5,
        "xǁConnectionManagerǁbroadcast__mutmut_6": xǁConnectionManagerǁbroadcast__mutmut_6,
        "xǁConnectionManagerǁbroadcast__mutmut_7": xǁConnectionManagerǁbroadcast__mutmut_7,
        "xǁConnectionManagerǁbroadcast__mutmut_8": xǁConnectionManagerǁbroadcast__mutmut_8,
        "xǁConnectionManagerǁbroadcast__mutmut_9": xǁConnectionManagerǁbroadcast__mutmut_9,
    }

    def broadcast(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁConnectionManagerǁbroadcast__mutmut_orig"),
            object.__getattribute__(
                self, "xǁConnectionManagerǁbroadcast__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    broadcast.__signature__ = _mutmut_signature(
        xǁConnectionManagerǁbroadcast__mutmut_orig
    )
    xǁConnectionManagerǁbroadcast__mutmut_orig.__name__ = (
        "xǁConnectionManagerǁbroadcast"
    )

    async def xǁConnectionManagerǁbroadcast_json__mutmut_orig(self, data: dict):
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_1(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if self.active_connections:
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_2(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info(None)
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_3(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("XXJSON broadcast requested, but no active connections.XX")
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_4(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("json broadcast requested, but no active connections.")
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_5(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON BROADCAST REQUESTED, BUT NO ACTIVE CONNECTIONS.")
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

    async def xǁConnectionManagerǁbroadcast_json__mutmut_6(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON broadcast requested, but no active connections.")
            return

        logger.info(None)
        tasks = [connection.send_json(data) for connection in self.active_connections]
        for task in tasks:
            try:
                await task
            except Exception as e:
                logger.warning(f"Failed to send JSON to a client: {e}")

    async def xǁConnectionManagerǁbroadcast_json__mutmut_7(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON broadcast requested, but no active connections.")
            return

        logger.info(
            f"Broadcasting JSON data to {len(self.active_connections)} clients."
        )
        tasks = None
        for task in tasks:
            try:
                await task
            except Exception as e:
                logger.warning(f"Failed to send JSON to a client: {e}")

    async def xǁConnectionManagerǁbroadcast_json__mutmut_8(self, data: dict):
        """
        Sends a JSON payload to all connected clients.
        """
        if not self.active_connections:
            logger.info("JSON broadcast requested, but no active connections.")
            return

        logger.info(
            f"Broadcasting JSON data to {len(self.active_connections)} clients."
        )
        tasks = [connection.send_json(None) for connection in self.active_connections]
        for task in tasks:
            try:
                await task
            except Exception as e:
                logger.warning(f"Failed to send JSON to a client: {e}")

    async def xǁConnectionManagerǁbroadcast_json__mutmut_9(self, data: dict):
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
            except Exception:
                logger.warning(None)

    xǁConnectionManagerǁbroadcast_json__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁConnectionManagerǁbroadcast_json__mutmut_1": xǁConnectionManagerǁbroadcast_json__mutmut_1,
        "xǁConnectionManagerǁbroadcast_json__mutmut_2": xǁConnectionManagerǁbroadcast_json__mutmut_2,
        "xǁConnectionManagerǁbroadcast_json__mutmut_3": xǁConnectionManagerǁbroadcast_json__mutmut_3,
        "xǁConnectionManagerǁbroadcast_json__mutmut_4": xǁConnectionManagerǁbroadcast_json__mutmut_4,
        "xǁConnectionManagerǁbroadcast_json__mutmut_5": xǁConnectionManagerǁbroadcast_json__mutmut_5,
        "xǁConnectionManagerǁbroadcast_json__mutmut_6": xǁConnectionManagerǁbroadcast_json__mutmut_6,
        "xǁConnectionManagerǁbroadcast_json__mutmut_7": xǁConnectionManagerǁbroadcast_json__mutmut_7,
        "xǁConnectionManagerǁbroadcast_json__mutmut_8": xǁConnectionManagerǁbroadcast_json__mutmut_8,
        "xǁConnectionManagerǁbroadcast_json__mutmut_9": xǁConnectionManagerǁbroadcast_json__mutmut_9,
    }

    def broadcast_json(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁConnectionManagerǁbroadcast_json__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁConnectionManagerǁbroadcast_json__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    broadcast_json.__signature__ = _mutmut_signature(
        xǁConnectionManagerǁbroadcast_json__mutmut_orig
    )
    xǁConnectionManagerǁbroadcast_json__mutmut_orig.__name__ = (
        "xǁConnectionManagerǁbroadcast_json"
    )


# --- Singleton Instance ---
# Create a single, globally accessible instance of the ConnectionManager.
connection_manager = ConnectionManager()
