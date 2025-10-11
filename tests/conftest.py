import asyncio
import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

# --- Session-wide Fixture to Set Test Environment ---
# Force the loading of test settings for the entire test session.
# This must be done at the module level, before any application code is imported.
os.environ["APP_ENV"] = "test"


# --- App Factory and Test Client Fixtures ---


@pytest.fixture(scope="function")
def test_app():
    """
    App Factory: Creates a fresh FastAPI instance for each test function.
    This prevents state leakage between tests and ensures that the app
    is created *after* the environment variables have been set.
    """
    # Import the app and its dependencies here to ensure the test environment is active
    from resync.main import app as main_app

    # Reset dependency overrides for a clean slate
    main_app.dependency_overrides = {}
    yield main_app


@pytest.fixture(scope="function")
def client(test_app: FastAPI) -> TestClient:
    """
    Provides a TestClient instance for a given app. This is the standard
    way to test endpoints without mocking dependencies.
    """
    with TestClient(test_app) as test_client:
        yield test_client


# --- Core Test Infrastructure Fixtures ---


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


class BackgroundTaskInterceptor:
    """A class to intercept and manage asyncio.create_task calls."""

    def __init__(self):
        self.captured_tasks = []
        self._real_create_task = asyncio.create_task
        self.capturing = False

    def start_capturing(self):
        """Start intercepting asyncio.create_task."""
        if not self.capturing:
            asyncio.create_task = self._capture_task
            self.capturing = True

    def stop_capturing(self):
        """Stop intercepting asyncio.create_task."""
        if self.capturing:
            asyncio.create_task = self._real_create_task
            self.capturing = False

    def _capture_task(self, coro, *, name=None):
        """The mock for asyncio.create_task that captures the coroutine."""
        self.captured_tasks.append((coro, (), {}))
        # Return a mock task object so the caller doesn't break
        return MagicMock(spec=asyncio.Task)

    def reset(self):
        """Clear all captured tasks."""
        self.captured_tasks = []

    @property
    def task_count(self):
        """Return the number of captured tasks."""
        return len(self.captured_tasks)

    async def run_all_async(self):
        """Execute all captured tasks asynchronously and return their results."""
        if not self.captured_tasks:
            return []

        tasks_to_run = self.captured_tasks
        self.reset()

        # Execute tasks with the real create_task function
        results = await asyncio.gather(
            *[self._real_create_task(coro) for coro, _, _ in tasks_to_run]
        )
        return results


@pytest.fixture
def background_tasks():
    """Pytest fixture to intercept and control asyncio background tasks."""
    interceptor = BackgroundTaskInterceptor()
    # The fixture should ensure that capturing is stopped after the test
    yield interceptor
    interceptor.stop_capturing()


# --- Mock Fixtures for Application Dependencies ---


@pytest.fixture
def mock_agent_manager():
    """Provides a mock IAgentManager."""
    from resync.core.interfaces import IAgentManager

    return AsyncMock(spec=IAgentManager)


@pytest.fixture
def mock_knowledge_graph():
    """Provides a mock IKnowledgeGraph."""
    from resync.core.interfaces import IKnowledgeGraph

    mock = AsyncMock(spec=IKnowledgeGraph)
    mock.get_all_recent_conversations = AsyncMock(return_value=[])
    # Mock the .session attribute for the async_knowledge_graph fixture
    mock.session = AsyncMock()
    return mock


@pytest.fixture
def mock_audit_queue():
    """Provides a mock IAuditQueue."""
    from resync.core.interfaces import IAuditQueue

    return AsyncMock(spec=IAuditQueue)


@pytest.fixture
def mock_tws_client():
    """Provides a mock OptimizedTWSClient."""
    from resync.core.interfaces import ITWSClient

    return AsyncMock(spec=ITWSClient)


@pytest.fixture
def mock_llm_call():
    """Provides a mock for the LLM call function."""
    return AsyncMock()


# --- Data Fixtures for Testing ---


@pytest.fixture
def security_test_data():
    """Provides common data for security tests."""
    return {
        "sql_injection": ["' OR 1=1; --", "UNION SELECT user, password FROM users"],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
        ],
        "malicious_headers": [
            {"X-Forwarded-For": "127.0.0.1"},
            {"Host": "malicious.com"},
        ],
    }


@pytest.fixture
def performance_test_data():
    """Provides common data for performance tests."""
    return {
        "iterations": 100,
        "concurrency": 10,
        # Corrected data structure to be a list of dicts with 'id'
        "large_dataset": [{"id": i} for i in range(1000)],
    }
