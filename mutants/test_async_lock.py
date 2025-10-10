#!/usr/bin/env python3

import asyncio
import time
from unittest.mock import MagicMock, patch

from resync.core.agent_manager import AgentManager


async def test_async_lock_functionality():
    """Test that the async lock prevents race conditions during TWS client initialization."""
    print("Testing async lock functionality...")

    # Reset singleton for test
    AgentManager._instance = None
    AgentManager._initialized = False
    agent_manager = AgentManager()

    # Mock the OptimizedTWSClient to track initialization calls
    init_call_count = 0
    mock_instance = MagicMock()

    def mock_tws_constructor(
        hostname, port, username, password, engine_name, engine_owner
    ):
        nonlocal init_call_count
        init_call_count += 1
        # Simulate some work
        time.sleep(0.1)
        return mock_instance

    with patch(
        "resync.core.agent_manager.OptimizedTWSClient", side_effect=mock_tws_constructor
    ):
        # Act - Create multiple concurrent tasks that all try to initialize the TWS client
        tasks = []
        for _i in range(5):
            task = asyncio.create_task(agent_manager._get_tws_client())
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # Assert
        # All tasks should return the same client instance
        assert all(
            result is mock_instance for result in results
        ), "All tasks should return the same instance"
        # But the initialization should only happen once
        assert (
            init_call_count == 1
        ), f"Initialization should only happen once, but happened {init_call_count} times"
        # The client should be stored in the agent manager
        assert (
            agent_manager.tws_client is mock_instance
        ), "Client should be stored in agent manager"

    print("✅ Async lock test passed!")
    print("✅ Race condition prevention working correctly!")
    return True


async def main():
    try:
        await test_async_lock_functionality()
        print("\n🎉 All tests passed! Async lock implementation is working correctly.")
        print("📋 Summary:")
        print("   - Added asyncio.Lock to prevent race conditions")
        print("   - Implemented double-check pattern in _get_tws_client()")
        print("   - Made TWS client initialization async-safe")
        print("   - Added comprehensive tests for race condition prevention")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
