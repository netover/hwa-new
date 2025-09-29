"""
Common test fixtures for the Resync application.
"""

import asyncio
from pathlib import Path
from typing import Generator, List, Tuple, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from resync.core.agent_manager import AgentManager
from resync.core.audit_queue import AsyncAuditQueue
from resync.core.connection_manager import ConnectionManager
from resync.core.di_container import DIContainer
from resync.core.file_ingestor import FileIngestor
from resync.core.interfaces import (
    IAgentManager,
    IAuditQueue,
    IConnectionManager,
    IFileIngestor,
    IKnowledgeGraph,
    ITWSClient,
)
from resync.core.knowledge_graph import AsyncKnowledgeGraph
from resync.services.tws_service import OptimizedTWSClient

# Lazy import to avoid issues during test collection
def _get_main_app():
    """Lazy import of main app to avoid initialization issues during test collection."""
    try:
        from resync.main import app as main_app
        return main_app
    except Exception:
        # Return a mock app if import fails
        from unittest.mock import MagicMock
        return MagicMock()

# --- Mock Service Fixtures ---


@pytest.fixture
def mock_agent_manager() -> MagicMock:
    """Create a mock AgentManager."""
    mock = MagicMock(spec=AgentManager)
    mock.agents = {}
    mock.agent_configs = []
    mock.tools = {}
    mock.tws_client = None
    mock._tws_init_lock = asyncio.Lock()
    mock.get_agent.return_value = MagicMock()
    mock.get_all_agents.return_value = []
    return mock


@pytest.fixture
def mock_tws_client() -> MagicMock:
    """Create a mock TWS Client."""
    mock = MagicMock(spec=OptimizedTWSClient)
    mock.base_url = "http://localhost:8080/twsd"
    mock.auth = ("test", "test")
    mock.engine_name = "test-engine"
    mock.engine_owner = "test-owner"
    mock.check_connection = AsyncMock(return_value=True)
    mock.get_workstations_status = AsyncMock(return_value=[])
    mock.get_jobs_status = AsyncMock(return_value=[])
    mock.get_critical_path_status = AsyncMock(return_value=[])
    mock.get_system_status = AsyncMock(return_value=MagicMock())
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_file_ingestor() -> MagicMock:
    """Create a mock FileIngestor."""
    mock = MagicMock(spec=FileIngestor)
    mock.rag_directory = Path("/tmp/rag")
    mock.save_uploaded_file = AsyncMock()
    mock.ingest_file = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_connection_manager() -> MagicMock:
    """Create a mock ConnectionManager."""
    mock = MagicMock(spec=ConnectionManager)
    mock.active_connections = []
    mock.connect = AsyncMock()
    mock.disconnect = AsyncMock()
    mock.broadcast = AsyncMock()
    mock.broadcast_json = AsyncMock()
    return mock


@pytest.fixture
def mock_knowledge_graph() -> MagicMock:
    """Create a mock KnowledgeGraph."""
    mock = MagicMock(spec=AsyncKnowledgeGraph)
    mock.data_dir = Path(".mem0")
    mock.client = MagicMock()
    mock.add_conversation = AsyncMock(return_value="mock-memory-id")
    mock.search_similar_issues = AsyncMock(return_value=[])
    mock.get_relevant_context = AsyncMock(return_value="Mock context")
    mock.is_memory_flagged = AsyncMock(return_value=False)
    mock.is_memory_approved = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_audit_queue() -> MagicMock:
    """Create a mock AuditQueue."""
    mock = MagicMock(spec=AsyncAuditQueue)
    mock.redis_url = "redis://localhost:6379"
    mock.sync_client = MagicMock()
    mock.async_client = MagicMock()
    mock.distributed_lock = MagicMock()
    mock.add_audit_record = AsyncMock(return_value=True)
    mock.get_pending_audits = AsyncMock(return_value=[])
    mock.update_audit_status = AsyncMock(return_value=True)
    mock.is_memory_approved = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Create a fully mocked Redis client for unit tests."""
    mock = MagicMock()
    # Configure default behaviors
    mock.keys.return_value = []
    mock.ttl.return_value = -1
    mock.exists.return_value = 0
    mock.delete.return_value = 1
    mock.hget.return_value = None
    mock.hset.return_value = 1
    mock.lpush.return_value = 1
    mock.lrange.return_value = []
    mock.llen.return_value = 0
    mock.pipeline.return_value = MagicMock()
    return mock


@pytest.fixture
def audit_queue(mock_redis_client: MagicMock) -> AsyncAuditQueue:
    """Create an AsyncAuditQueue instance with mocked Redis for testing."""
    # Create AsyncAuditQueue instance
    queue = AsyncAuditQueue.__new__(
        AsyncAuditQueue
    )  # Don't call __init__ to avoid Redis connection

    # Set up the instance attributes
    queue.redis_url = "redis://localhost:6379"
    queue.audit_queue_key = "resync:audit_queue"
    queue.audit_status_key = "resync:audit_status"
    queue.audit_data_key = "resync:audit_data"

    # Use the mocked Redis client
    queue.redis_client = mock_redis_client
    queue.sync_client = mock_redis_client
    queue.async_client = mock_redis_client

    # Create a mock distributed lock that can be awaited
    mock_lock = AsyncMock()
    mock_lock.cleanup_expired_locks = AsyncMock(return_value=0)  # Default: no locks cleaned
    mock_lock.acquire = AsyncMock()
    mock_lock.force_release = AsyncMock()
    queue.distributed_lock = mock_lock

    return queue


# --- DI Container Fixtures ---


@pytest.fixture
def test_container(
    mock_agent_manager: MagicMock,
    mock_connection_manager: MagicMock,
    mock_knowledge_graph: MagicMock,
    mock_audit_queue: MagicMock,
    mock_tws_client: MagicMock,
    mock_file_ingestor: MagicMock,
) -> DIContainer:
    """Create a test DI container with mock services."""
    container = DIContainer()

    # Register interfaces with mock implementations
    container.register_instance(IAgentManager, mock_agent_manager)
    container.register_instance(IConnectionManager, mock_connection_manager)
    container.register_instance(IKnowledgeGraph, mock_knowledge_graph)
    container.register_instance(IAuditQueue, mock_audit_queue)
    container.register_instance(ITWSClient, mock_tws_client)
    container.register_instance(IFileIngestor, mock_file_ingestor)

    # Register concrete types as well
    container.register_instance(AgentManager, mock_agent_manager)
    container.register_instance(ConnectionManager, mock_connection_manager)
    container.register_instance(AsyncKnowledgeGraph, mock_knowledge_graph)
    container.register_instance(AsyncAuditQueue, mock_audit_queue)
    container.register_instance(OptimizedTWSClient, mock_tws_client)
    container.register_instance(FileIngestor, mock_file_ingestor)

    return container


@pytest.fixture
def app_with_di_container(test_container: DIContainer) -> FastAPI:
    """Create a FastAPI app with the test DI container."""
    from resync.core.fastapi_di import inject_container

    # Create a copy of the main app
    app = FastAPI()

    # Copy routes from the main app (lazy import to avoid issues)
    try:
        main_app = _get_main_app()
        for route in main_app.routes:
            app.routes.append(route)
    except Exception:
        # If main app import fails, continue without routes
        pass

    # Inject the test container
    inject_container(app, test_container)

    return app


@pytest.fixture
def test_client(app_with_di_container: FastAPI) -> TestClient:
    """Create a TestClient with the app using the test DI container."""
    return TestClient(app_with_di_container)


# --- Legacy Fixtures and Patches ---


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create a mock settings object."""
    mock = MagicMock()
    mock.AGENT_CONFIG_PATH = Path("tests/fixtures/test_agents.json")
    mock.TWS_HOST = "localhost"
    mock.TWS_PORT = 8080
    mock.TWS_USER = "test"
    mock.TWS_PASSWORD = "test"
    mock.TWS_ENGINE_NAME = "test"
    mock.TWS_ENGINE_OWNER = "test"
    mock.MEM0_STORAGE_HOST = "localhost"
    mock.MEM0_STORAGE_PORT = 6333
    mock.MEM0_EMBEDDING_PROVIDER = "mock"
    mock.MEM0_EMBEDDING_MODEL = "mock"
    mock.MEM0_LLM_PROVIDER = "mock"
    mock.MEM0_LLM_MODEL = "mock"
    return mock


@pytest.fixture
def patch_settings(mock_settings: MagicMock) -> Generator[None, None, None]:
    """Patch the global settings with a mock."""
    with (
        patch("resync.core.agent_manager.settings", mock_settings),
        patch("resync.core.knowledge_graph.settings", mock_settings),
        patch("resync.core.audit_queue.settings", mock_settings),
    ):
        yield


@pytest.fixture(scope="module")
def redis_client():
    """Create a real Redis client for integration tests."""
    import redis
    from redis.exceptions import ConnectionError

    # Try to connect to Redis
    client = redis.Redis.from_url("redis://localhost:6379")

    # Test connection
    try:
        client.ping()
    except ConnectionError as e:
        raise RuntimeError("Redis server not available") from e

    yield client

    # Cleanup (not strictly necessary as Redis handles this)
    client.disconnect()


@pytest.fixture(scope="function")
def clean_redis(redis_client):
    """Fixture that provides a cleaned Redis instance for each test."""
    # Store current DB keys
    keys = redis_client.keys("resync:*")

    yield redis_client

    # Restore state by deleting any new keys
    if keys:
        redis_client.delete(*keys)
    else:
        # Clear all resync keys
        redis_client.delete(*redis_client.keys("resync:*"))


# --- Background Tasks Fixture ---


class BackgroundTasksFixture:
    """Fixture for capturing and testing background tasks."""

    def __init__(self):
        self._capturing = False
        self._original_create_task = None
        self.captured_tasks: List[Tuple[Any, tuple, dict]] = []

    def start_capturing(self):
        """Start intercepting asyncio.create_task calls."""
        if not self._capturing:
            self._original_create_task = asyncio.create_task
            # Don't clear captured_tasks here - let reset() handle it
            self._capturing = True

            def capture_task(coro, *args, **kwargs):
                """Capture task creation instead of executing it."""
                if self._capturing:
                    self.captured_tasks.append((coro, args, kwargs))
                    # Return a mock task that never completes
                    return asyncio.Future()
                else:
                    return self._original_create_task(coro, *args, **kwargs)

            asyncio.create_task = capture_task

    def stop_capturing(self):
        """Stop intercepting asyncio.create_task calls."""
        if self._capturing:
            asyncio.create_task = self._original_create_task
            self._capturing = False

    def reset(self):
        """Clear all captured tasks."""
        # Cancel any pending futures to avoid warnings
        for coro, args, kwargs in self.captured_tasks:
            if hasattr(coro, 'close'):
                try:
                    coro.close()
                except:
                    pass
        self.captured_tasks = []

    @property
    def task_count(self) -> int:
        """Return the number of captured tasks."""
        return len(self.captured_tasks)

    async def run_all_async(self) -> List[Any]:
        """Execute all captured tasks asynchronously and return their results."""
        results = []
        for coro, args, kwargs in self.captured_tasks:
            if asyncio.iscoroutine(coro):
                result = await coro
            else:
                # If it's not a coroutine, try to call it
                if callable(coro):
                    if asyncio.iscoroutinefunction(coro):
                        result = await coro(*args, **kwargs)
                    else:
                        result = coro(*args, **kwargs)
                else:
                    result = coro
            results.append(result)
        return results

    def run_all_sync(self) -> List[Any]:
        """Execute all captured tasks synchronously and return their results."""
        # This is a simple synchronous version - in practice you'd want proper event loop handling
        results = []
        for coro, args, kwargs in self.captured_tasks:
            if asyncio.iscoroutine(coro):
                # For sync execution, we'll need to use asyncio.run or similar
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, we can't use run_until_complete
                        # This is a limitation of the current implementation
                        results.append(coro)
                    else:
                        result = loop.run_until_complete(coro)
                        results.append(result)
                except RuntimeError:
                    results.append(coro)
            else:
                results.append(coro)
        return results


@pytest.fixture
def background_tasks():
    """Create a background tasks fixture for testing."""
    fixture = BackgroundTasksFixture()

    yield fixture

    # Cleanup: restore original create_task if it was patched
    if fixture._capturing:
        fixture.stop_capturing()


@pytest.fixture
def performance_test_data():
    """Create performance test data for testing."""
    # Generate a large dataset for performance testing
    large_dataset = [
        {"id": i, "data": f"performance_test_data_{i}" * 100}
        for i in range(1000)
    ]

    return {
        "large_dataset": large_dataset,
        "test_config": {
            "batch_size": 100,
            "concurrency": 10,
            "timeout": 30
        }
    }
