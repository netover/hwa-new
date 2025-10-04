
"""
Tests for connection pool exhaustion scenarios and graceful degradation.

This module tests how the connection pooling system behaves when:
- Connection pools are exhausted (max connections reached)
- Resources are unavailable
- Timeout scenarios occur
- Fallback mechanisms activate
- Circuit breakers trigger
- Load balancing under stress
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from resync.core.connection_pool_manager import (
    ConnectionPoolConfig,
    ConnectionTimeoutError,
    DatabaseConnectionPool,
    HTTPConnectionPool,
    PoolExhaustedError,
    RedisConnectionPool,
)
from resync.core.exceptions import (
    DatabaseError,
    TWSConnectionError,
)
from resync.core.websocket_pool_manager import WebSocketPoolManager
from resync.settings import settings


class TestDatabasePoolExhaustion:
    """Test database connection pool exhaustion scenarios."""

    @pytest_asyncio.fixture
    async def constrained_db_pool(self):
        """Create a database pool with limited connections for exhaustion testing."""
        config = ConnectionPoolConfig(
            pool_name="exhaustion_test_db",
            min_size=1,
            max_size=3,  # Very limited for testing exhaustion
            timeout=2,   # Short timeout to test timeouts quickly
            retry_attempts=2,
            retry_delay=0.1,
        )

        # Mock database engine to simulate real behavior
        with patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine

            pool = DatabaseConnectionPool(config, "sqlite:///:memory:")
            await pool.initialize()
            yield pool
            await pool.shutdown()

    @pytest.mark.asyncio
    async def test_database_pool_exhaustion_timeout(self, constrained_db_pool):
        """Test behavior when database pool is exhausted and requests timeout."""
        # Acquire all available connections
        connections = []

        for _i in range(3):  # Acquire all 3 connections
            conn = await constrained_db_pool._create_connection()
            connections.append(conn)

        # Try to get another connection - should timeout
        start_time = time.time()

        with pytest.raises(ConnectionTimeoutError):
            async with constrained_db_pool.get_connection():
                pass

        timeout_duration = time.time() - start_time

        # Should timeout within configured timeout period
        assert timeout_duration <= 3.0  # Allow small buffer
        assert timeout_duration >= 1.5   # Should wait for timeout

        # Clean up connections
        for conn in connections:
            await constrained_db_pool._close_connection(conn)

    @pytest.mark.asyncio
    async def test_database_pool_graceful_degradation(self, constrained_db_pool):
        """Test graceful degradation when database pool is under stress."""
        results = []

        async def database_operation_with_fallback(operation_id: int):
            """Database operation with fallback mechanism."""
            try:
                async with constrained_db_pool.get_connection():
                    # Simulate database work
                    await asyncio.sleep(0.1)
                    results.append(f"db_success_{operation_id}")
                    return "database"
            except (PoolExhaustedError, ConnectionTimeoutError):
                # Fallback to cache or read-only replica
                results.append(f"fallback_success_{operation_id}")
                return "fallback"
            except Exception as e:
                results.append(f"error_{operation_id}_{str(e)}")
                return "error"

        # Create more requests than pool can handle
        num_operations = 10
        tasks = [database_operation_with_fallback(i) for i in range(num_operations)]

        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        # Should have some fallback responses due to pool exhaustion
        fallback_count = sum(1 for outcome in outcomes if outcome == "fallback")
        db_count = sum(1 for outcome in outcomes if outcome == "database")

        assert fallback_count > 0  # Some operations should use fallback
        assert db_count > 0        # Some should succeed with database
        assert len(results) == num_operations

    @pytest.mark.asyncio
    async def test_database_pool_recovery_after_exhaustion(self, constrained_db_pool):
        """Test pool recovery after exhaustion."""
        # First, exhaust the pool
        held_connections = []

        async def hold_connection(duration: float):
            """Hold a connection for specified duration."""
            async with constrained_db_pool.get_connection() as engine:
                held_connections.append(engine)
                await asyncio.sleep(duration)

        # Exhaust pool
        hold_tasks = [hold_connection(0.5) for _ in range(3)]

        # Try to get connection while pool is exhausted
        async def try_connection():
            try:
                async with constrained_db_pool.get_connection():
                    return "success"
            except (PoolExhaustedError, ConnectionTimeoutError):
                return "exhausted"

        # Start holding connections
        hold_task = asyncio.create_task(asyncio.gather(*hold_tasks))

        # Wait a bit then try to connect
        await asyncio.sleep(0.1)
        result = await try_connection()
        assert result == "exhausted"

        # Wait for connections to be released
        await hold_task

        # Pool should recover
        await asyncio.sleep(0.1)  # Allow cleanup

        result = await try_connection()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_database_pool_circuit_breaker(self, constrained_db_pool):
        """Test circuit breaker behavior with database pool."""
        error_count = 0
        success_count = 0

        # Simulate database failures
        with patch.object(constrained_db_pool, '_validate_connection', side_effect=DatabaseError("Connection failed")):
            async def database_operation_with_circuit_breaker(operation_id: int):
                """Database operation with circuit breaker pattern."""
                nonlocal error_count, success_count

                # Circuit breaker logic
                if error_count > 5:  # Open circuit
                    return "circuit_open"

                try:
                    async with constrained_db_pool.get_connection():
                        success_count += 1
                        return "success"
                except DatabaseError:
                    error_count += 1
                    return "database_error"
                except (PoolExhaustedError, ConnectionTimeoutError):
                    return "pool_error"

            # Run operations until circuit opens
            results = []
            for i in range(20):
                result = await database_operation_with_circuit_breaker(i)
                results.append(result)

                if result == "circuit_open":
                    break

            # Circuit should open after enough errors
            assert "circuit_open" in results
            assert error_count > 5


class TestRedisPoolExhaustion:
    """Test Redis connection pool exhaustion scenarios."""

    @pytest_asyncio.fixture
    async def constrained_redis_pool(self):
        """Create a Redis pool with limited connections."""
        config = ConnectionPoolConfig(
            pool_name="exhaustion_test_redis",
            min_size=1,
            max_size=2,  # Very limited
            timeout=1,
            retry_attempts=1,
            retry_delay=0.05,
        )

        with patch('redis.asyncio.ConnectionPool.from_url') as mock_from_url:
            mock_pool = MagicMock()
            mock_from_url.return_value = mock_pool

            pool = RedisConnectionPool(config, "redis://localhost:6379/1")
            await pool.initialize()
            yield pool
            await pool.shutdown()

    @pytest.mark.asyncio
    async def test_redis_pool_rate_limiting_exhaustion(self, constrained_redis_pool):
        """Test Redis pool exhaustion during rate limiting operations."""
        rate_limit_hits = 0
        rate_limit_misses = 0

        async def rate_limit_check(client_id: str):
            """Rate limiting operation that might exhaust pool."""
            nonlocal rate_limit_hits, rate_limit_misses

            try:
                async with constrained_redis_pool.get_connection():
                    # Simulate Redis rate limit check
                    await asyncio.sleep(0.01)

                    # Simulate rate limit decision
                    allowed = True  # In real scenario, this would check Redis
                    if allowed:
                        rate_limit_hits += 1
                    else:
                        rate_limit_misses += 1

                    return allowed

            except (PoolExhaustedError, ConnectionTimeoutError):
                # Rate limit check failed due to pool exhaustion
                # Should we allow or deny? Conservative approach: deny
                rate_limit_misses += 1
                return False

        # Simulate burst of rate limit checks
        num_checks = 20
        tasks = [rate_limit_check(f"client_{i}") for i in range(num_checks)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should have some rate limit checks
        assert rate_limit_hits > 0
        assert rate_limit_misses > 0
        assert len([r for r in results if r is True]) == rate_limit_hits
        assert len([r for r in results if r is False]) == rate_limit_misses

    @pytest.mark.asyncio
    async def test_redis_pool_cache_fallback(self, constrained_redis_pool):
        """Test cache fallback when Redis pool is exhausted."""
        cache_hits = 0
        cache_misses = 0
        fallback_count = 0

        async def get_cached_data(key: str):
            """Get data from cache with fallback."""
            nonlocal cache_hits, cache_misses, fallback_count

            try:
                async with constrained_redis_pool.get_connection():
                    # Simulate cache lookup
                    await asyncio.sleep(0.005)

                    # Simulate cache hit/miss
                    if key.startswith("cached_"):
                        cache_hits += 1
                        return {"data": f"cached_{key}", "source": "redis"}
                    else:
                        cache_misses += 1
                        return None

            except (PoolExhaustedError, ConnectionTimeoutError):
                # Fallback to local cache or database
                fallback_count += 1
                await asyncio.sleep(0.01)  # Simulate slower fallback
                return {"data": f"fallback_{key}", "source": "fallback"}

        # Test with mixed cache scenarios
        keys = ["cached_1", "cached_2", "uncached_1", "cached_3", "uncached_2"]

        # Run multiple times to trigger pool exhaustion
        results = []
        for _i in range(10):
            batch_tasks = [get_cached_data(key) for key in keys]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

        # Should have variety of results
        redis_results = [r for r in results if r and r.get("source") == "redis"]
        fallback_results = [r for r in results if r and r.get("source") == "fallback"]

        assert len(redis_results) > 0  # Some Redis cache hits
        assert len(fallback_results) > 0  # Some fallback due to pool exhaustion


class TestHTTPPoolExhaustion:
    """Test HTTP connection pool exhaustion scenarios."""

    @pytest_asyncio.fixture
    async def constrained_http_pool(self):
        """Create an HTTP pool with limited connections."""
        config = ConnectionPoolConfig(
            pool_name="exhaustion_test_http",
            min_size=1,
            max_size=3,  # Limited connections
            timeout=2,
            retry_attempts=2,
            retry_delay=0.1,
        )

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.is_closed = False

            # Mock response for health checks
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_instance.head.return_value = mock_response

            pool = HTTPConnectionPool(config, "https://api.example.com")
            await pool.initialize()
            yield pool
            await pool.shutdown()

    @pytest.mark.asyncio
    async def test_http_pool_api_exhaustion(self, constrained_http_pool):
        """Test HTTP pool exhaustion during API calls."""
        api_success = 0
        api_failures = 0

        async def api_call_with_retry(endpoint: str, max_retries: int = 3):
            """API call with retry logic."""
            nonlocal api_success, api_failures

            for attempt in range(max_retries):
                try:
                    async with constrained_http_pool.get_connection() as client:
                        # Mock successful response
                        mock_response = MagicMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {"status": "success"}

                        client.get.return_value = mock_response

                        response = await client.get(endpoint)

                        if response.status_code == 200:
                            api_success += 1
                            return response
                        else:
                            api_failures += 1

                except (PoolExhaustedError, ConnectionTimeoutError):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        continue
                    else:
                        api_failures += 1
                        return None
                except Exception:
                    api_failures += 1
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (2 ** attempt))
                        continue
                    else:
                        return None

        # Simulate burst of API calls
        num_calls = 15
        endpoints = [f"/api/endpoint/{i}" for i in range(num_calls)]

        tasks = [api_call_with_retry(endpoint) for endpoint in endpoints]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Should have some successful calls despite pool limitations
        assert api_success > 0
        assert api_failures < num_calls  # Not all should fail

        success_rate = api_success / num_calls
        assert success_rate > 0.3  # At least 30% success rate

    @pytest.mark.asyncio
    async def test_http_pool_circuit_breaker_integration(self, constrained_http_pool):
        """Test HTTP pool with circuit breaker pattern."""
        consecutive_failures = 0
        circuit_open = False

        async def api_call_with_circuit_breaker(endpoint: str):
            """API call with circuit breaker integration."""
            nonlocal consecutive_failures, circuit_open

            # Check circuit breaker
            if circuit_open:
                return {"error": "Circuit breaker open", "fallback": True}

            try:
                async with constrained_http_pool.get_connection() as client:
                    # Simulate API call with potential failure
                    if consecutive_failures > 3:  # Simulate service degradation
                        raise TWSConnectionError("Service unavailable")

                    # Mock successful response
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"data": "success"}

                    client.get.return_value = mock_response

                    response = await client.get(endpoint)
                    consecutive_failures = 0  # Reset on success

                    return {"data": response.json(), "source": "api"}

            except (PoolExhaustedError, ConnectionTimeoutError):
                # Circuit breaker should prevent cascading failures
                consecutive_failures += 1
                if consecutive_failures > 5:
                    circuit_open = True
                return {"error": "Pool exhausted", "fallback": True}

            except TWSConnectionError:
                consecutive_failures += 1
                if consecutive_failures > 5:
                    circuit_open = True
                return {"error": "Service error", "fallback": True}

        # Test circuit breaker behavior
        num_calls = 20
        results = []

        for i in range(num_calls):
            result = await api_call_with_circuit_breaker(f"/api/test/{i}")
            results.append(result)

            # Add small delay to simulate real-world timing
            await asyncio.sleep(0.01)

        # Circuit breaker should eventually open
        assert circuit_open is True

        # Should have fallback responses after circuit opens
        fallback_results = [r for r in results if r.get("fallback") is True]
        assert len(fallback_results) > 0


class TestWebSocketPoolExhaustion:
    """Test WebSocket connection pool exhaustion scenarios."""

    @pytest_asyncio.fixture
    async def ws_manager(self):
        """Create WebSocket pool manager for exhaustion testing."""
        manager = WebSocketPoolManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_websocket_connection_limit(self, ws_manager):
        """Test WebSocket connection limits."""
        # Set low connection limit for testing
        original_limit = settings.WS_MAX_CONNECTIONS
        settings.WS_MAX_CONNECTIONS = 5

        connections = []

        async def create_websocket_connection(client_id: str):
            """Create WebSocket connection."""
            try:
                mock_websocket = AsyncMock()
                mock_websocket.client_state.DISCONNECTED = False

                await ws_manager.connect(mock_websocket, client_id)
                connections.append(client_id)

                # Keep connection alive
                await asyncio.sleep(0.1)

                return "connected"

            except Exception as e:
                return f"connection_failed_{str(e)}"

        # Try to create more connections than limit
        num_attempts = 10
        tasks = [create_websocket_connection(f"client_{i}") for i in range(num_attempts)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Should have limited number of successful connections
        successful_connections = [r for r in results if r == "connected"]

        assert len(successful_connections) <= settings.WS_MAX_CONNECTIONS

        # Clean up
        for client_id in connections:
            await ws_manager.disconnect(client_id)

        # Restore original limit
        settings.WS_MAX_CONNECTIONS = original_limit

    @pytest.mark.asyncio
    async def test_websocket_broadcast_under_load(self, ws_manager):
        """Test WebSocket broadcasting when pool is under load."""
        # Create multiple connections
        connections = []

        for i in range(5):
            mock_websocket = AsyncMock()
            mock_websocket.client_state.DISCONNECTED = False
            await ws_manager.connect(mock_websocket, f"client_{i}")
            connections.append(mock_websocket)

        # Test broadcast under simulated load
        messages_sent = 0
        messages_failed = 0

        async def broadcast_with_monitoring(message: str):
            """Broadcast message and monitor results."""
            nonlocal messages_sent, messages_failed

            try:
                successful_sends = await ws_manager.broadcast(message)
                messages_sent += successful_sends
                return successful_sends
            except Exception:
                messages_failed += 1
                return 0

        # Send multiple broadcasts
