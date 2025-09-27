"""
Core Interfaces for Resync

This module defines the interfaces for the core components of the Resync application.
These interfaces are used with the dependency injection system to decouple
components and make them more testable.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from fastapi import WebSocket

from resync.core.agent_manager import AgentConfig


@runtime_checkable
class IAgentManager(Protocol):
    """Interface for the AgentManager component."""

    agents: Dict[str, Any]
    agent_configs: List[AgentConfig]
    tools: Dict[str, Any]
    tws_client: Any
    _tws_init_lock: asyncio.Lock

    async def load_agents_from_config(self, config_path: Path) -> None:
        """Load agent configurations from a file."""
        ...

    async def _get_tws_client(self) -> Any:
        """Get the TWS client instance."""
        ...

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an agent by ID."""
        ...

    def get_all_agents(self) -> List[AgentConfig]:
        """Get all agent configurations."""
        ...

    def get_agent_with_tool(self, agent_id: str, tool_name: str) -> Optional[Any]:
        """Get an agent that has a specific tool."""
        ...


@runtime_checkable
class IConnectionManager(Protocol):
    """Interface for the ConnectionManager component."""

    active_connections: List[WebSocket]

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        ...

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        ...

    async def broadcast(self, message: str) -> None:
        """Send a message to all connected clients."""
        ...

    async def broadcast_json(self, data: Dict[str, Any]) -> None:
        """Send a JSON payload to all connected clients."""
        ...


@runtime_checkable
class IKnowledgeGraph(Protocol):
    """Interface for the KnowledgeGraph component."""

    data_dir: Path
    client: Any

    async def add_conversation(
        self,
        user_query: str,
        agent_response: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a conversation in the knowledge graph."""
        ...

    async def search_similar_issues(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar issues in the knowledge graph."""
        ...

    async def get_relevant_context(self, user_query: str) -> str:
        """Get relevant context for a user query."""
        ...

    async def add_solution_feedback(
        self, memory_id: str, feedback: str, rating: int
    ) -> None:
        """Add user feedback to a memory."""
        ...

    async def is_memory_flagged(self, memory_id: str) -> bool:
        """Check if a memory is flagged."""
        ...

    async def is_memory_approved(self, memory_id: str) -> bool:
        """Check if a memory is approved."""
        ...

    async def delete_memory(self, memory_id: str) -> None:
        """Delete a memory."""
        ...

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        """Add observations to a memory."""
        ...


@runtime_checkable
class IAuditQueue(Protocol):
    """Interface for the AuditQueue component."""

    redis_url: str
    sync_client: Any
    async_client: Any
    distributed_lock: Any
    audit_queue_key: str
    audit_status_key: str
    audit_data_key: str

    async def add_audit_record(self, memory: Dict[str, Any]) -> bool:
        """Add a memory to the audit queue."""
        ...

    async def get_pending_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending audits from the queue."""
        ...

    async def update_audit_status(self, memory_id: str, status: str) -> bool:
        """Update the status of an audit record."""
        ...

    async def is_memory_approved(self, memory_id: str) -> bool:
        """Check if a memory is approved."""
        ...

    async def delete_audit_record(self, memory_id: str) -> bool:
        """Remove an audit record."""
        ...

    async def get_queue_length(self) -> int:
        """Get the length of the audit queue."""
        ...

    async def get_all_audits(self) -> List[Dict[str, Any]]:
        """Get all audit records."""
        ...

    async def get_audits_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get audit records by status."""
        ...

    async def get_audit_metrics(self) -> Dict[str, int]:
        """Get metrics for the audit queue."""
        ...

    async def health_check(self) -> bool:
        """Check if Redis is accessible."""
        ...

    def get_all_audits_sync(self) -> List[Dict[str, Any]]:
        """Synchronous wrapper for get_all_audits."""
        ...

    def update_audit_status_sync(self, memory_id: str, status: str) -> bool:
        """Synchronous wrapper for update_audit_status."""
        ...


@runtime_checkable
class IFileIngestor(Protocol):
    """Interface for the File Ingestor component."""

    rag_directory: Path

    async def ingest_file(self, file_path: Path) -> bool:
        """Ingests a file into the knowledge graph."""
        ...

    async def save_uploaded_file(self, file_name: str, file_content) -> Path:
        """Saves an uploaded file to the RAG directory."""
        ...


@runtime_checkable
class ITWSClient(Protocol):
    """Interface for the TWS Client component."""

    base_url: str
    auth: tuple
    engine_name: str
    engine_owner: str
    client: Any
    cache: Any

    async def check_connection(self) -> bool:
        """Verifies the connection to the TWS server is active."""
        ...

    async def get_workstations_status(self) -> List[Any]:
        """Retrieves the status of all workstations."""
        ...

    async def get_jobs_status(self) -> List[Any]:
        """Retrieves the status of all jobs."""
        ...

    async def get_critical_path_status(self) -> List[Any]:
        """Retrieves the status of jobs in the critical path."""
        ...

    async def get_system_status(self) -> Any:
        """Retrieves a comprehensive system status."""
        ...

    async def close(self) -> None:
        """Closes the underlying client and its connections."""
        ...


# Additional interfaces can be added as needed
