
"""
Comprehensive unit tests for connection pooling implementation.

This module tests all aspects of the connection pooling system including:
- Database connection pool (PostgreSQL/MySQL/SQLite compatible)
- Redis connection pool for caching and rate limiting
- HTTP connection pool for external API calls
- WebSocket connection pool optimization
- Connection pool manager lifecycle management
- Pool statistics and monitoring
- Connection leak detection
- Performance benchmarking
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import pytest_asyncio

from resync.core.connection_pool_manager import (
    ConnectionPoolConfig,
    ConnectionPoolManager,
    ConnectionPoolStats,
    DatabaseConnectionPool,
    HTTPConnectionPool,
    RedisConnectionPool,
    get_connection_pool_manager,
    shutdown_connection_pool_manager,
)
from resync.core.websocket_pool_manager import (
    WebSocketPoolManager,
    get_websocket_pool_manager,
    shutdown_websocket_pool_manager,
)
from resync.settings import settings


class TestConnectionPoolConfig:
    """Test connection pool configuration."""

    def test_default_config(self):
        """Test default configuration values."""
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

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ConnectionPoolConfig(
            pool_name="custom_pool",
            min_size=10,
            max_size=50,
            timeout=60,
            retry_attempts=5,
            retry_delay=2,
            health_check_interval=30,
            idle_timeout=600,
        )

        assert config.pool_name == "custom_pool"
        assert config.min_size == 10
        assert config.max_size == 50
        assert config.timeout == 60
        assert config.retry_attempts == 5
        assert config.retry_delay == 2
        assert config.health_check_interval == 30
        assert config.idle_timeout == 600


class TestConnectionPoolStats:
    """Test connection pool statistics."""

    def test_default_stats(self):
        """Test default statistics values."""
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


class TestDatabaseConnectionPool:
    """Test database connection pool implementation."""

    @pytest_asyncio.fixture
    async def db_pool(self):
        """Create a test database connection pool."""
        config = ConnectionPoolConfig(
            pool_name="test_database",
            min_size=2,
            max_size=5,
            timeout=10,
        )
        database_url = "sqlite:///:memory:"
        pool = DatabaseConnectionPool(config, database_url)
        await pool.initialize()
        yield pool
        await pool.shutdown()

    @pytest.mark.asyncio
    async def test_database_pool_initialization(self, db_pool):
        """Test database pool initialization."""
        assert db_pool._initialized is True
        assert db_pool._engine is not None

    @pytest.mark.asyncio
    async def test_database_pool_health_check(self, db_pool):
        """Test database pool health check."""
        is_healthy = await db_pool.health_check()
        assert is_healthy is True

        stats = db_pool.get_stats()
        assert stats.last_health_check is not None

    @pytest.mark.asyncio
    async def test_database_pool_connection_acquisition(self, db_pool):
        """Test acquiring database connections from pool."""
        async with db_pool.get_connection() as engine:
            assert engine is not None

        # Check that stats were updated
        stats = db_pool.get_stats()
        assert stats.pool_hits >= 1

    @pytest.mark.asyncio
    async def test_database_pool_connection_validation(self, db_pool):
        """Test database connection validation."""
        engine = await db_pool._create_connection()
        is_valid = await db_pool._validate_connection(engine)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_database_pool_concurrent_connections(self, db_pool):
        """Test concurrent database connections."""
        async def use_connection(connection_id):
            async with db_pool.get_connection():
                # Simulate some work
                await asyncio.sleep(0.1)
                return f"connection_{connection_id}"

        # Create multiple concurrent connections
        tasks = [use_connection(i) for i in range(3)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all("connection_" in result for result in results)

    @pytest.mark.asyncio
    async def test_database_pool_shutdown(self, db_pool):
        """Test database pool shutdown."""
        await db_pool.shutdown()
        assert db_pool._initialized is False
        assert db_pool._shutdown is True


class TestRedisConnectionPool:
    """Test Redis connection pool implementation."""

    @pytest_asyncio.fixture
    async def redis_pool(self):
        """Create a test Redis connection pool with mock."""
        config = ConnectionPoolConfig(
            pool_name="test_redis",
            min_size=2,
            max_size=5,
            timeout=10,
        )

        with patch('redis.asyncio.ConnectionPool.from_url') as mock_from_url:
            mock_pool = MagicMock()
            mock_from_url.return_value = mock_pool

            pool = RedisConnectionPool(config, "redis://localhost:6379/1")
            await pool.initialize()
            yield pool
            await pool.shutdown()

    @pytest.mark.asyncio
    async def test_redis_pool_initialization(self, redis_pool):
        """Test Redis pool initialization."""
        assert redis_pool._initialized is True
        assert redis_pool._connection_pool is not None

    @pytest.mark.asyncio
    async def test_redis_pool_health_check(self, redis_pool):
        """Test Redis pool health check."""
        with patch.object(redis_pool, '_validate_connection', return_value=True):
            is_healthy = await redis_pool.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_redis_pool_connection_acquisition(self, redis_pool):
        """Test acquiring Redis connections from pool."""
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client

            async with redis_pool.get_connection() as connection:
                assert connection is not None

            # Verify close was called
            mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_pool_connection_validation(self, redis_pool):
        """Test Redis connection validation."""
        mock_connection = AsyncMock()
        mock_connection.ping.return_value = True

        is_valid = await redis_pool._validate_connection(mock_connection)
        assert is_valid is True
        mock_connection.ping.assert_called_once()


class TestHTTPConnectionPool:
    """Test HTTP connection pool implementation."""

    @pytest_asyncio.fixture
    async def http_pool(self):
        """Create a test HTTP connection pool."""
        config = ConnectionPoolConfig(
            pool_name="test_http",
            min_size=2,
            max_size=10,
            timeout=10,
        )

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.is_closed = False

            pool = HTTPConnectionPool(config, "https://api.example.com")
            await pool.initialize()
            yield pool
            await pool.shutdown()

    @pytest.mark.asyncio
    async def test_http_pool_initialization(self, http_pool):
        """Test HTTP pool initialization."""
        assert http_pool._initialized is True
        assert http_pool._client is not None

    @pytest.mark.asyncio
    async def test_http_pool_health_check(self, http_pool):
        """Test HTTP pool health check."""
        with patch.object(http_pool._client, 'head') as mock_head:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_head.return_value = mock_response

            is_healthy = await http_pool.health_check()
            assert is_healthy is True

    @pytest.mark.asyncio
    async def test_http_pool_connection_acquisition(self, http_pool):
        """Test acquiring HTTP connections from pool."""
        async with http_pool.get_connection() as client:
            assert client is not None

        # Check that stats were updated
        stats = http_pool.get_stats()
        assert stats.pool_hits >= 1


class TestConnectionPoolManager:
    """Test the central connection pool manager."""

    @pytest_asyncio.fixture
    async def pool_manager(self):
        """Create a test connection pool manager."""
        manager = ConnectionPoolManager()

        # Mock the pool initialization to avoid actual connections
        with patch.object(manager, '_setup_pool'):
            with patch.object(manager, 'health_check', return_value=True):
                await manager.initialize()
                yield manager
                await manager.shutdown()

    @pytest.mark.asyncio
    async def test_pool_manager_initialization(self, pool_manager):
        """Test connection pool manager initialization."""
        assert pool_manager._initialized is True
        assert pool_manager._shutdown is False

    @pytest.mark.asyncio
    async def test_pool_manager_get_pool(self, pool_manager):
        """Test getting specific pool from manager."""
        # Add a mock pool
        mock_pool = Mock()
        pool_manager.pools["test_pool"] = mock_pool

        retrieved_pool = pool_manager.get_pool("test_pool")
        assert retrieved_pool == mock_pool

        # Test non-existent pool
        non_existent = pool_manager.get_pool("non_existent")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_pool_manager_get_all_pools(self, pool_manager):
        """Test getting all pools from manager."""
        # Add mock pools
        mock_pool1 = Mock()
        mock_pool2 = Mock()
        pool_manager.pools["pool1"] = mock_pool1
        pool_manager.pools["pool2"] = mock_pool2

        all_pools = pool_manager.get_all_pools()
        assert len(all_pools) == 2
        assert "pool1" in all_pools
        assert "pool2" in all_pools

    @pytest.mark.asyncio
    async def test_pool_manager_health_check_all(self, pool_manager):
        """Test health check on all pools."""
        # Add mock pools
        mock_pool1 = Mock()
        mock_pool1.health_check = AsyncMock(return_value=True)
        mock_pool2 = Mock()
        mock_pool2.health_check = AsyncMock(return_value=False)

        pool_manager.pools["pool1"] = mock_pool1
        pool_manager.pools["pool2"] = mock_pool2

        results = await pool_manager.health_check_all()
        assert results["pool1"] is True
        assert results["pool2"] is False

    @pytest.mark.asyncio
    async def test_pool_manager_is_healthy(self, pool_manager):
        """Test overall health check of pool manager."""
        # Add healthy mock pool
        mock_pool = Mock()
        mock_stats = Mock()
        mock_stats.connection_errors = 2  # Below threshold
        mock_pool.get_stats.return_value = mock_stats

        pool_manager.pools["healthy_pool"] = mock_pool

        is_healthy = pool_manager.is_healthy()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_pool_manager_is_unhealthy(self, pool_manager):
        """Test unhealthy pool manager detection."""
        # Add unhealthy mock pool
        mock_pool = Mock()
        mock_stats = Mock()
        mock_stats.connection_errors = 10  # Above threshold
        mock_pool.get_stats.return_value = mock_stats

        pool_manager.pools["unhealthy_pool"] = mock_pool

        is_healthy = pool_manager.is_healthy()
        assert is_healthy is False


class TestWebSocketPoolManager:
    """Test WebSocket connection pool manager."""

    @pytest_asyncio.fixture
    async def ws_manager(self):
        """Create a test WebSocket pool manager."""
        manager = WebSocketPoolManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_websocket_pool_initialization(self, ws_manager):
        """Test WebSocket pool manager initialization."""
        assert ws_manager._initialized is True
        assert ws_manager._shutdown is False

    @pytest.mark.asyncio
    async def test_websocket_connection_management(self, ws_manager):
        """Test WebSocket connection management."""
        # Create mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.client_state.DISCONNECTED = False

        # Add connection
        await ws_manager.connect(mock_websocket, "test_client")
        assert "test_client" in ws_manager.connections
        assert ws_manager.stats.active_connections == 1

        # Remove connection
        await ws_manager.disconnect("test_client")
        assert "test_client" not in ws_manager.connections
        assert ws_manager.stats.active_connections == 0

    @pytest.mark.asyncio
    async def test_websocket_personal_message(self, ws_manager):
        """Test sending personal messages."""
        # Create mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.client_state.DISCONNECTED = False

        await ws_manager.connect(mock_websocket, "test_client")

        # Send personal message
        success = await ws_manager.send_personal_message("Hello", "test_client")
        assert success is True

        # Verify message was sent
        mock_websocket.send_text.assert_called_once_with("Hello")

    @pytest.mark.asyncio
    async def test_websocket_broadcast(self, ws_manager):
        """Test broadcasting messages."""
        # Create mock WebSockets
        mock_websocket1 = AsyncMock()
        mock_websocket1.client_state.DISCONNECTED = False
        mock_websocket2 = AsyncMock()
        mock_websocket2.client_state.DISCONNECTED = False

        await ws_manager.connect(mock_websocket1, "client1")
        await ws_manager.connect(mock_websocket2, "client2")

        # Broadcast message
        successful_sends = await ws_manager.broadcast("Broadcast message")
        assert successful_sends == 2

        # Verify messages were sent
        mock_websocket1.send_text.assert_called_once_with("Broadcast message")
        mock_websocket2.send_text.assert_called_once_with("Broadcast message")

    @pytest.mark.asyncio
    async def test_websocket_cleanup(self, ws_manager):
        """Test WebSocket connection cleanup."""
        # Create mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.client_state.DISCONNECTED = False

        await ws_manager.connect(mock_websocket, "test_client")

        # Simulate stale connection
        old_time = datetime.now() - timedelta(seconds=settings.WS_CONNECTION_TIMEOUT + 1)
        ws_manager.connections["test_client"].last_activity = old_time

        # Run cleanup
        await ws_manager._cleanup_connections()

        # Verify connection was removed
        assert "test_client" not in ws_manager.connections
        assert ws_manager.stats.cleanup_cycles == 1

    @pytest.mark.asyncio
    async def test_websocket_health_check(self, ws_manager):
        """Test WebSocket pool health check."""
        # Should be healthy with no connections
        is_healthy = await ws_manager.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_websocket_health_check_unhealthy(self, ws_manager):
        """Test unhealthy WebSocket pool detection."""
        # Create unhealthy connection
        mock_websocket = AsyncMock()
        mock_websocket.client_state.DISCONNECTED = False

        await ws_manager.connect(mock_websocket, "test_client")

        # Mark as unhealthy
        ws_manager.connections["test_client"].is_healthy = False
        ws_manager.connections["test_client"].connection_errors = 10
        ws_manager.stats.unhealthy_connections = 1

        # Should be unhealthy
        is_healthy = await ws_manager.health_check()
        assert is_healthy is False


class TestConnectionPoolIntegration:
    """Test integration of all connection pool components."""

    @pytest.mark.asyncio
    async def test_global_pool_manager_lifecycle(self):
        """Test global connection pool manager lifecycle."""
        # Initialize global manager
        manager = await get_connection_pool_manager()
        assert manager is not None
        assert manager._initialized is True

        # Shutdown global manager
        await shutdown_connection_pool_manager()

        # Verify shutdown
        # Note: The global instance should be None after shutdown
        # but we can't easily test this without affecting other tests

    @pytest.mark.asyncio
    async def test_global_websocket_manager_lifecycle(self):
        """Test global WebSocket pool manager lifecycle."""
        # Initialize global manager
        manager = await get_websocket_pool_manager()
        assert manager is not None
        assert manager._initialized is True

        # Shutdown global manager
        await shutdown_websocket_pool_manager()

    @pytest.mark.asyncio
    async def test_pool_manager_with_mock_pools(self):
        """Test pool manager with mock pools."""
        manager = ConnectionPoolManager()

        # Mock pool creation
        with patch.object(manager, '_setup_pool'):
            with patch.object(manager, 'health_check', return_value=True):
                await manager.initialize()

                # Add mock pools
                mock_db_pool = Mock()
                mock_redis_pool = Mock()

                manager.pools["database"] = mock_db_pool
                manager.pools["redis"] = mock_redis_pool

                # Test pool retrieval
                db_pool = manager.get_pool("database")
                redis_pool = manager.get_pool("redis")

                assert db_pool == mock_db_pool
                assert redis_pool == mock_redis_pool

                await manager.shutdown()


class TestConnectionPoolPerformance:
    """Test connection pool performance characteristics."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_connection_pool_concurrent_access(self):
        """Test concurrent access to connection pools."""
        # Create a pool with limited connections
        config = ConnectionPoolConfig(
            pool_name="performance_test",
            min_size=2,
            max_size=5,
            timeout=5,
        )

        # Mock database pool for performance testing
        with patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine

            pool = DatabaseConnectionPool(config, "sqlite:///:memory:")
            await pool.initialize()

            results = []

            async def concurrent_operation(op_id):
                try:
                    async with pool.get_connection():
                        await asyncio.sleep(0.001)  # Simulate work
                        results.append(f"op_{op_id}")
                        return True
                except Exception:
                    return False

            # Run concurrent operations
            tasks = [concurrent_operation(i) for i in range(20)]
            outcomes = await asyncio.gather(*tasks)

            # Should handle concurrent access
            successful = sum(1 for outcome in outcomes if outcome is True)
            assert successful >= 15  # At least 75% success rate

            await pool.shutdown()
