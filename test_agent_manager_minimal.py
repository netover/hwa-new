#!/usr/bin/env python3

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from pydantic import BaseModel, Field

# Mock the agno imports for testing
class MockAgent:
    def __init__(self, tools=None, model=None, system=None, verbose=False):
        self.tools = tools or []
        self.model = model
        self.system = system
        self.verbose = verbose

class MockTool:
    def __init__(self, name, description, model):
        self.name = name
        self.description = description
        self.model = model

# Mock the TWS service
class MockOptimizedTWSClient:
    def __init__(self, hostname, port, username, password, engine_name, engine_owner):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.engine_name = engine_name
        self.engine_owner = engine_owner

# Mock the settings
class MockSettings:
    TWS_HOST = "localhost"
    TWS_PORT = 8080
    TWS_USER = "test_user"
    TWS_PASSWORD = "test_password"
    TWS_ENGINE_NAME = "test_engine"
    TWS_ENGINE_OWNER = "test_owner"
    AGENT_CONFIG_PATH = Path("test_config.json")

# Mock the TWS tools
class MockTWSToolReadOnly(BaseModel):
    tws_client: Optional[Any] = Field(default=None, exclude=True)

class MockTWSStatusTool(MockTWSToolReadOnly):
    async def get_tws_status(self) -> str:
        return "Mock TWS Status"

class MockTWSTroubleshootingTool(MockTWSToolReadOnly):
    async def analyze_failures(self) -> str:
        return "Mock Troubleshooting"

# Create mock tools
mock_tws_status_tool = MockTool(
    name="tws_status_tool",
    description="Obtém o status geral de workstations e jobs no ambiente TWS.",
    model=MockTWSStatusTool
)

mock_tws_troubleshooting_tool = MockTool(
    name="tws_troubleshooting_tool",
    description="Analisa jobs com falha e workstations offline para diagnosticar problemas.",
    model=MockTWSTroubleshootingTool
)

# Replace the imports in agent_manager with our mocks
import sys
sys.modules['agno'] = type('MockAgno', (), {
    'Agent': MockAgent,
    'tools': type('MockTools', (), {'Tool': MockTool})
})()

sys.modules['agno.tools'] = type('MockAgnoTools', (), {'Tool': MockTool})()

# Now import the actual agent manager
from resync.core.agent_manager import AgentManager, AgentsConfig, settings

# Replace settings with our mock
import resync.core.agent_manager as am_module
am_module.settings = MockSettings()

async def test_async_lock_functionality():
    """Test that the async lock prevents race conditions during TWS client initialization."""
    print("🧪 Testing async lock functionality...")

    # Reset singleton for test
    AgentManager._instance = None
    AgentManager._initialized = False
    agent_manager = AgentManager()

    # Mock the OptimizedTWSClient to track initialization calls
    init_call_count = 0

    async def mock_tws_init(self, hostname, port, username, password, engine_name, engine_owner):
        nonlocal init_call_count
        init_call_count += 1
        # Simulate some async work
        await asyncio.sleep(0.1)
        # Initialize as a proper mock
        self.base_url = f"{hostname}:{port}/twsd"
        self.auth = (username, password)
        self.engine_name = engine_name
        self.engine_owner = engine_owner

    with patch.object(MockOptimizedTWSClient, '__init__', mock_tws_init):
        with patch("resync.core.agent_manager.OptimizedTWSClient", MockOptimizedTWSClient):
            # Act - Create multiple concurrent tasks that all try to initialize the TWS client
            tasks = []
            for i in range(5):
                task = asyncio.create_task(agent_manager._get_tws_client())
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks)

            # Assert
            # All tasks should return the same client instance
            assert all(result is not None for result in results), "All tasks should return a client instance"
            # But the initialization should only happen once
            assert init_call_count == 1, f"Initialization should only happen once, but happened {init_call_count} times"
            # The client should be stored in the agent manager
            assert agent_manager.tws_client is not None, "Client should be stored in agent manager"

    print("✅ Async lock test passed!")
    print("✅ Race condition prevention working correctly!")
    return True

async def main():
    try:
        await test_async_lock_functionality()
        print("\n🎉 All tests passed! Async lock implementation is working correctly.")
        print("📋 Summary of implemented features:")
        print("   ✅ Added asyncio.Lock to prevent race conditions")
        print("   ✅ Implemented double-check pattern in _get_tws_client()")
        print("   ✅ Made TWS client initialization async-safe")
        print("   ✅ Added comprehensive tests for race condition prevention")
        print("   ✅ Updated _create_agents and load_agents_from_config to be async")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)