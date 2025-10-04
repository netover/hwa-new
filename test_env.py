"""
Simple validation test for connection pooling implementation.
This test bypasses the complex environment setup and focuses on the core functionality.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch

# Set minimal required environment variables
os.environ['ADMIN_USERNAME'] = 'test_admin'
os.environ['ADMIN_PASSWORD'] = 'test_password'
os.environ['ENVIRONMENT'] = 'test'

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_connection_pool_config():
    """Test basic connection pool configuration."""
    try:
        from resync.core.connection_pool_manager import ConnectionPoolConfig

        # Test default configuration
        config = ConnectionPoolConfig(pool_name="test_pool")

        assert config.pool_name == "test_pool"
        assert config.min_size == 5
        assert config.max_size == 20
        assert config.timeout == 30
        assert config.retry_attempts == 3
        assert config.retry_delay == 1
        assert config.health_check_interval == 60
        assert config.idle_timeout == 300
        assert config.enabled is True

        print("✓ ConnectionPoolConfig default values test passed")

        # Test custom configuration
        custom_config = ConnectionPoolConfig(
            pool_name="custom_pool",
            min_size=10,
            max_size=50,
            timeout=60,
            retry_attempts=5,
            retry_delay=2,
            health_check_interval=30,
            idle_timeout=600,
        )

        assert custom_config.pool_name == "custom_pool"
        assert custom_config.min_size == 10
        assert custom_config.max_size == 50
        assert custom_config.timeout == 60
        assert custom_config.retry_attempts == 5
        assert custom_config.retry_delay == 2
        assert custom_config.health_check_interval == 30
        assert custom_config.idle_timeout == 600

        print("✓ ConnectionPoolConfig custom values test passed")

        return True

    except Exception as e:
        print(f"✗ ConnectionPoolConfig test failed: {e}")
        return False

async def test_connection_pool_stats():
    """Test connection pool statistics."""
    try:
        from resync.core.connection_pool_manager import ConnectionPoolStats

        stats = ConnectionPoolStats(pool_name="test_pool")

        assert stats.pool_name == "test_pool"
        assert stats.active_connections == 0
        assert stats.idle_connections == 0
        assert stats.total_connections == 0
        assert stats.waiting_connections == 0
        assert stats.connection_errors == 0
        assert stats.connection_creations == 0
        assert stats.connection_closures == 0
        assert stats.pool_hits == 0
        assert stats.pool_misses == 0
        assert stats.pool_exhaustions == 0
        assert stats.last_health_check is None
        assert stats.average_wait_time == 0.0
        assert stats.peak_connections == 0

        print("✓ ConnectionPoolStats test passed")
        return True

    except Exception as e:
        print(f"✗ ConnectionPoolStats test failed: {e}")
        return False

async def test_pool_manager_creation():
    """Test connection pool manager creation."""
    try:
        from resync.core.connection_pool_manager import ConnectionPoolManager

        with patch.object(ConnectionPoolManager, '_setup_pool'):
            with patch.object(ConnectionPoolManager, 'health_check', return_value=True):
                manager = ConnectionPoolManager()
                await manager.initialize()

                assert manager._initialized is True
                assert manager._shutdown is False

                await manager.shutdown()
                assert manager._shutdown is True

        print("✓ ConnectionPoolManager lifecycle test passed")
        return True

    except Exception as e:
        print(f"✗ ConnectionPoolManager test failed: {e}")
        return False

async def test_websocket_pool_manager():
    """Test WebSocket pool manager."""
    try:
        from resync.core.websocket_pool_manager import WebSocketPoolManager

        manager = WebSocketPoolManager()
        await manager.initialize()

        assert manager._initialized is True
        assert manager._shutdown is False

        # Test basic WebSocket operations
        mock_websocket = AsyncMock()
        mock_websocket.client_state.DISCONNECTED = False

        await manager.connect(mock_websocket, "test_client")
        assert "test_client" in manager.connections
        assert manager.stats.active_connections == 1

        await manager.disconnect("test_client")
        assert "test_client" not in manager.connections
        assert manager.stats.active_connections == 0

        await manager.shutdown()
        assert manager._shutdown is True

        print("✓ WebSocketPoolManager test passed")
        return True

    except Exception as e:
        print(f"✗ WebSocketPoolManager test failed: {e}")
        return False

async def main():
    """Run all validation tests."""
    print("Running connection pooling validation tests...")
    print("=" * 50)

    tests = [
        test_connection_pool_config,
        test_connection_pool_stats,
        test_pool_manager_creation,
        test_websocket_pool_manager,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if await test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All connection pooling tests passed!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
