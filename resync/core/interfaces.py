"""Interfaces for Resync components."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IKnowledgeGraph(Protocol):
    """
    Interface for the Knowledge Graph service.
    Defines methods for interacting with the knowledge graph.
    """

    async def add_content(self, content: str, metadata: Dict[str, Any]) -> str:
        ...

    async def add_conversation(
        self,
        user_query: str,
        agent_response: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    async def search_similar_issues(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        ...

    async def search_conversations(
        self,
        query: str = "type:conversation",
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        ...

    async def add_solution_feedback(
        self, memory_id: str, feedback: str, rating: int
    ) -> None:
        ...

    async def get_all_recent_conversations(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
        ...

    async def get_relevant_context(self, user_query: str) -> str:
        ...

    async def is_memory_flagged(self, memory_id: str) -> bool:
        ...

    async def is_memory_approved(self, memory_id: str) -> bool:
        ...

    async def delete_memory(self, memory_id: str) -> None:
        ...

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        ...

    async def is_memory_already_processed(self, memory_id: str) -> bool:
        ...

    async def atomic_check_and_flag(
        self, memory_id: str, reason: str, confidence: float
    ) -> bool:
        ...

    async def atomic_check_and_delete(self, memory_id: str) -> bool:
        ...


@runtime_checkable
class IFileIngestor(Protocol):
    """
    Interface for the File Ingestor service.
    """

    async def save_uploaded_file(self, file_name: str, file_content: Any) -> Path:
        ...

    async def ingest_file(self, file_path: Path) -> bool:
        ...


@runtime_checkable
class IAgentManager(Protocol):
    """Interface for managing AI agents."""

    async def load_agents_from_config(self) -> None:
        ...

    async def get_agent(self, agent_id: str) -> Any:
        ...


@runtime_checkable
class IConnectionManager(Protocol):
    """Interface for managing WebSocket connections."""

    async def connect(self, websocket: Any, client_id: str) -> None:
        ...

    async def disconnect(self, client_id: str) -> None:
        ...

    async def broadcast(self, message: str) -> None:
        ...

    async def send_personal_message(self, message: str, client_id: str) -> None:
        ...


@runtime_checkable
class IAuditQueue(Protocol):
    """Interface for an audit queue."""

    async def add_audit_record(self, record: Dict[str, Any]) -> None:
        ...


@runtime_checkable
class ITWSMonitor(Protocol):
    """Interface for the TWS Monitor service."""

    async def start_monitoring(self) -> None:
        ...

    async def stop_monitoring(self) -> None:
        ...

    def get_performance_report(self) -> Dict[str, Any]:
        ...

    def get_alerts(self, limit: int) -> List[Dict[str, Any]]:
        ...

    async def health_check(self) -> Dict[str, Any]:
        ...


@runtime_checkable
class ITWSClient(Protocol):
    """Interface for the TWS client."""

    async def get_system_status(self) -> Dict[str, Any]:
        ...

    @property
    def is_connected(self) -> bool:
        ...

    async def close(self) -> None:
        ...


@runtime_checkable
class ICircuitBreaker(Protocol):
    """Interface for the Circuit Breaker pattern."""

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        ...

    def get_stats(self) -> Dict[str, Any]:
        ...


@runtime_checkable
class ILLMCostMonitor(Protocol):
    """Interface for the LLM Cost Monitor."""

    async def track_request(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        response_time: float,
        success: bool = True,
    ) -> None:
        ...

    def get_usage_report(self) -> Dict[str, Any]:
        ...


@runtime_checkable
class ICircuitBreakerManager(Protocol):
    """Interface for the Circuit Breaker Manager."""

    def get_breaker(self, operation: str) -> ICircuitBreaker:
        ...

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        ...