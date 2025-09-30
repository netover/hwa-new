"""
Shared pytest configuration and fixtures.
"""

import pytest
import asyncio
from pathlib import Path
from resync.core.di_container import DIContainer


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_path(tmp_path):
    """Provide a temporary path for testing."""
    return tmp_path


@pytest.fixture
def di_container():
    """Provide a fresh DI container for testing."""
    container = DIContainer()
    return container


@pytest.fixture(scope="session")
def test_settings():
    """Mock settings for testing."""
    class MockSettings:
        APP_ENV = "development"
        TWS_HOST = "localhost"
        TWS_PORT = 4001
        AGENT_MODEL_NAME = "test-model"
        LLM_ENDPOINT = "http://localhost:8000"
        AGENT_CONFIG_PATH = "/tmp/test_config.json"
        RAG_DIR = "/tmp/test_rag"

    return MockSettings()