"""
Configuration file for pytest fixtures.
This module provides shared fixtures for all tests in the project.
"""

import asyncio
from typing import Any, Callable, List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class BackgroundTasksFixture:
    """
    A fixture for capturing and manually executing background tasks.

    This fixture can intercept calls to asyncio.create_task() and store
    the coroutines for later manual execution in tests.
    """

    def __init__(self):
        self._captured_tasks: List[Tuple[Callable, tuple, dict]] = []
        self._original_create_task = asyncio.create_task
        self._patcher = None

    def _capture_task(self, coro, *args, **kwargs):
        """
        Capture a task created with asyncio.create_task().

        Args:
            coro: The coroutine to be executed as a task
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            A mock task object
        """
        # Store the coroutine and its arguments for later execution
        self._captured_tasks.append((coro, args, kwargs))

        # Return a mock task to avoid actually scheduling it
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_task.cancelled.return_value = False
        return mock_task

    def start_capturing(self):
        """Start intercepting calls to asyncio.create_task()."""
        if self._patcher is None:
            self._patcher = patch("asyncio.create_task", side_effect=self._capture_task)
            self._patcher.start()

    def stop_capturing(self):
        """Stop intercepting calls to asyncio.create_task()."""
        if self._patcher is not None:
            self._patcher.stop()
            self._patcher = None

    def reset(self):
        """Clear all captured tasks."""
        self._captured_tasks.clear()

    @property
    def captured_tasks(self) -> List[Tuple[Any, tuple, dict]]:
        """
        Get the list of captured tasks.

        Returns:
            List of tuples containing (coroutine, args, kwargs)
        """
        return self._captured_tasks.copy()

    @property
    def task_count(self) -> int:
        """Get the number of captured tasks."""
        return len(self._captured_tasks)

    async def run_all_async(self):
        """
        Execute all captured tasks asynchronously.

        This method runs all captured tasks concurrently and waits for them to complete.
        """
        if not self._captured_tasks:
            return []

        # Create actual tasks from the captured coroutines
        tasks = []
        for coro, args, kwargs in self._captured_tasks:
            if asyncio.iscoroutine(coro):
                task = self._original_create_task(coro, *args, **kwargs)
                tasks.append(task)
            else:
                # If it's a callable that returns a coroutine
                if callable(coro):
                    result = coro(*args, **kwargs)
                    if asyncio.iscoroutine(result):
                        task = self._original_create_task(result)
                        tasks.append(task)

        # Run all tasks concurrently and wait for completion
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        return []

    def run_all_sync(self):
        """
        Execute all captured tasks synchronously.

        This method attempts to run all captured tasks in the current event loop.
        Note: This might not work for all types of coroutines.
        """
        import asyncio

        if not self._captured_tasks:
            return []

        results = []
        for coro, args, kwargs in self._captured_tasks:
            try:
                if asyncio.iscoroutine(coro):
                    # For actual coroutines, we need to run them in the event loop
                    result = asyncio.run_coroutine_threadsafe(
                        coro, asyncio.get_event_loop()
                    ).result()
                    results.append(result)
                else:
                    # For callable objects
                    if callable(coro):
                        result = coro(*args, **kwargs)
                        if asyncio.iscoroutine(result):
                            result = asyncio.run_coroutine_threadsafe(
                                result, asyncio.get_event_loop()
                            ).result()
                        results.append(result)
            except Exception as e:
                results.append(e)

        return results


@pytest.fixture
async def background_tasks():
    """
    Pytest fixture for capturing and manually executing background tasks.

    This fixture intercepts calls to asyncio.create_task() and allows tests
    to manually control when background tasks are executed.

    Usage:
        async def test_something(background_tasks):
            # Start capturing tasks
            background_tasks.start_capturing()

            # Code that creates background tasks
            asyncio.create_task(some_async_function())

            # Manually execute captured tasks
            results = await background_tasks.run_all_async()

            # Or execute synchronously
            # results = background_tasks.run_all_sync()
    """
    fixture = BackgroundTasksFixture()
    yield fixture
    # Cleanup
    fixture.stop_capturing()
    fixture.reset()


# Additional fixtures for comprehensive testing


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.delete.return_value = 1
    return mock_client


@pytest.fixture
def mock_llm():
    """Mock LLM service for testing."""
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Mock response"
    mock_llm.analyze.return_value = {
        "sentiment": "positive",
        "confidence": 0.9,
    }
    return mock_llm


@pytest.fixture
def mock_audit_db():
    """Mock audit database for testing."""
    mock_db = MagicMock()
    mock_db.insert_audit_record.return_value = "audit_id_123"
    mock_db.get_audit_records.return_value = []
    mock_db.update_audit_status.return_value = True
    return mock_db


@pytest.fixture
def mock_agent_manager():
    """Mock agent manager for testing dependency injection."""
    mock_manager = MagicMock()
    mock_manager.get_instance.return_value = MagicMock()
    mock_manager.create_agent.return_value = MagicMock()
    mock_manager.cleanup.return_value = None
    return mock_manager


@pytest.fixture
def security_test_data():
    """Test data for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; SELECT * FROM users WHERE '1'='1",
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
        ],
        "malicious_headers": {
            "X-Forwarded-For": "192.168.1.1, 127.0.0.1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    }


@pytest.fixture
def performance_test_data():
    """Test data for performance testing."""
    return {
        "large_dataset": [{"id": i, "data": f"test_data_{i}"} for i in range(1000)],
        "stress_concurrent_users": 100,
        "stress_duration_seconds": 60,
        "memory_threshold_mb": 500,
    }


@pytest.fixture
def async_test_context():
    """Context manager for async testing."""
    return {
        "event_loop": asyncio.get_event_loop(),
        "timeout": 30.0,
        "max_concurrent": 10,
    }


@pytest.fixture(scope="session", autouse=True)
def mock_redis_global():
    """Global mock for Redis clients to prevent real connections in tests."""
    with (
        patch("redis.asyncio.Redis", new_callable=AsyncMock) as mock_async_redis,
        patch("redis.Redis", new_callable=MagicMock) as mock_sync_redis,
    ):
        # Configure async mock
        mock_async_redis.return_value.ping.return_value = True
        mock_async_redis.return_value.set.return_value = True
        mock_async_redis.return_value.get.return_value = None
        mock_async_redis.return_value.delete.return_value = 1
        mock_async_redis.return_value.eval.return_value = 1
        mock_async_redis.return_value.evalsha.return_value = 1
        mock_async_redis.return_value.script_load.return_value = "mock_sha"
        mock_async_redis.return_value.keys.return_value = []
        mock_async_redis.return_value.ttl.return_value = 0
        mock_async_redis.return_value.flushdb.return_value = True
        mock_async_redis.return_value.aclose.return_value = None

        # Configure sync mock (if used)
        mock_sync_redis.return_value.ping.return_value = True
        mock_sync_redis.return_value.set.return_value = True
        mock_sync_redis.return_value.get.return_value = None
        mock_sync_redis.return_value.delete.return_value = 1
        mock_sync_redis.return_value.eval.return_value = 1
        mock_sync_redis.return_value.evalsha.return_value = 1
        mock_sync_redis.return_value.script_load.return_value = "mock_sha"
        mock_sync_redis.return_value.keys.return_value = []
        mock_sync_redis.return_value.ttl.return_value = 0
        mock_sync_redis.return_value.flushdb.return_value = True
        mock_sync_redis.return_value.close.return_value = None

        yield
