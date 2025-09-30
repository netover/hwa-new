import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
import fakeredis.aioredis

from resync.core.agent_manager import AgentManager


class BackgroundTasks:
    """A fixture to capture and manage background tasks created with asyncio.create_task."""

    def __init__(self):
        self.captured_tasks = []
        self._capturing = False
        self._original_create_task = asyncio.create_task

    def start_capturing(self):
        self.reset()
        self._capturing = True
        asyncio.create_task = self._capture_task

    def stop_capturing(self):
        self._capturing = False
        asyncio.create_task = self._original_create_task

    def _capture_task(self, coro, *, name=None):
        if self._capturing:
            # Store the coroutine and its arguments for later execution
            task = self._original_create_task(coro, name=name)
            self.captured_tasks.append(task)
            return task
        return self._original_create_task(coro, name=name)

    async def run_all_async(self):
        """Manually execute all captured tasks."""
        return await asyncio.gather(*self.captured_tasks)

    def reset(self):
        # Cancel any pending tasks before clearing
        for task in self.captured_tasks:
            if not task.done():
                task.cancel()
        self.captured_tasks = []

    @property
    def task_count(self):
        return len(self.captured_tasks)


@pytest.fixture(scope="function")
def background_tasks():
    """Pytest fixture to capture and control background tasks."""
    task_manager = BackgroundTasks()
    yield task_manager
    # Teardown: stop capturing and restore original function
    task_manager.stop_capturing()


@pytest.fixture
def mock_agent_manager():
    """Mocks the AgentManager for testing purposes."""
    manager = MagicMock(spec=AgentManager)
    manager.get_agent = AsyncMock()
    manager.get_all_agents = AsyncMock()
    manager.load_agents_from_config = AsyncMock()
    manager._get_tws_client = AsyncMock()
    return manager


@pytest.fixture
def mock_tws_client():
    """Mocks the OptimizedTWSClient."""
    return AsyncMock()


@pytest.fixture
def mock_knowledge_graph():
    """Mocks the AsyncKnowledgeGraph."""
    return AsyncMock()


@pytest.fixture
def mock_audit_queue():
    """Mocks the AsyncAuditQueue."""
    return AsyncMock()


@pytest.fixture
def mock_llm_call():
    """Mocks the call_llm function."""
    return AsyncMock()


@pytest.fixture
def performance_test_data():
    """Provides data for performance tests."""
    return {}


@pytest.fixture
def security_test_data():
    """Provides data for security tests."""
    return {}


@pytest.fixture
def mock_redis_client():
    """Mocks the redis client."""
    return fakeredis.aioredis.FakeRedis()