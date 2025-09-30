"""Interfaces for Resync components."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from resync.core.agent_manager import AgentConfig


@runtime_checkable
class IKnowledgeGraph(Protocol):
    """
    Interface for the Knowledge Graph service.
    Defines methods for interacting with the knowledge graph.
    """

    async def add_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """Adds a piece of content (e.g., a document chunk) to the knowledge graph."""
        ...

    async def add_conversation(
        self,
        user_query: str,
        agent_response: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Stores a conversation between a user and an agent."""
        ...

    async def search_similar_issues(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches the knowledge graph for similar past issues and solutions."""
        ...

    async def search_conversations(
        self,
        query: str = "type:conversation",
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """Optimized search method for conversations."""
        ...

    async def add_solution_feedback(
        self, memory_id: str, feedback: str, rating: int
    ) -> None:
        """Adds user feedback to a specific memory."""
        ...

    async def get_all_recent_conversations(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieves all recent conversation-type memories for auditing."""
        ...

    async def get_relevant_context(self, user_query: str) -> str:
        """Retrieves a structured text summary of relevant knowledge from the graph."""
        ...

    async def is_memory_flagged(self, memory_id: str) -> bool:
        """Checks if a memory has been flagged by the IA Auditor."""
        ...

    async def is_memory_approved(self, memory_id: str) -> bool:
        """Checks if a memory has been approved by an admin."""
        ...

    async def delete_memory(self, memory_id: str) -> None:
        """Deletes a memory from the knowledge graph."""
        ...

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        """Adds observations to a memory in the knowledge graph."""
        ...

    async def is_memory_already_processed(self, memory_id: str) -> bool:
        """Atomically checks if a memory has already been processed."""
        ...

    async def atomic_check_and_flag(
        self, memory_id: str, reason: str, confidence: float
    ) -> bool:
        """Atomically checks if memory is already processed, and if not, flags it."""
        ...

    async def atomic_check_and_delete(self, memory_id: str) -> bool:
        """Atomically checks if memory is already processed, and if not, deletes it."""
        ...


@runtime_checkable
class IFileIngestor(Protocol):
    """
    Interface for the File Ingestor service.
    Defines methods for handling file uploads, saving, and processing for RAG.
    """

    async def save_uploaded_file(self, file_name: str, file_content: Any) -> Path:
        """Saves an uploaded file to the RAG directory."""
        ...

    async def ingest_file(self, file_path: Path) -> bool:
        """Ingests a single file into the knowledge graph."""
        ...


@runtime_checkable
class IAgentManager(Protocol):
    """Interface for managing AI agents."""

    async def load_agents_from_config(self) -> None:
        """Loads agent configurations."""
        ...

    async def get_agent(self, agent_id: str) -> Any:
        """Retrieves an agent by its ID."""
        ...

    async def get_all_agents(self) -> List["AgentConfig"]:
        """Returns the configuration of all loaded agents."""
        ...


@runtime_checkable
class IConnectionManager(Protocol):
    """Interface for managing WebSocket connections."""

    async def connect(self, websocket: Any, client_id: str) -> None:
        """Handles a new WebSocket connection."""
        ...

    async def disconnect(self, client_id: str) -> None:
        """Handles a disconnected WebSocket client."""
        ...

    async def broadcast(self, message: str) -> None:
        """Broadcasts a message to all connected clients."""
        ...

    async def send_personal_message(self, message: str, client_id: str) -> None:
        """Sends a message to a specific client."""
        ...


@runtime_checkable
class IAuditQueue(Protocol):
    """Interface for an audit queue."""

    async def add_audit_record(self, record: Dict[str, Any]) -> None:
        """Adds an audit record to the queue."""
        ...


@runtime_checkable
class ITWSClient(Protocol):
    """Interface for the TWS client."""

    async def get_system_status(self) -> Dict[str, Any]:
        """Retrieves the current TWS system status."""
        ...

    @property
    def is_connected(self) -> bool:
        """Checks if the TWS client is currently connected."""
        ...

    async def close(self) -> None:
        """Closes the TWS client connection."""
        ...