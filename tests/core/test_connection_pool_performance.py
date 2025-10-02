
"""
Performance benchmarking tests for connection pooling implementation.

This module contains comprehensive performance tests to validate:
- Connection pool throughput under various load conditions
- Concurrent connection handling and resource utilization
- Pool exhaustion scenarios and graceful degradation
- Memory usage and leak detection
- Response time and latency measurements
- Connection acquisition/release performance
- Pool scaling behavior
"""

import asyncio
import pytest
import time
import gc
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from resync.core.connection_pool_manager import (
    ConnectionPoolManager,
    DatabaseConnectionPool,
    RedisConnectionPool,
    HTTPConnectionPool,
    ConnectionPoolConfig,
    ConnectionPoolStats,
)
from resync.core.websocket_pool_manager import WebSocketPoolManager, WebSocketConnectionInfo
from resync.core.exceptions import DatabaseError, TWSConnectionError
from resync.settings import settings


class ConnectionPoolBenchmark:
    """Benchmark utility for connection pool performance testing."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'acquisition_time': [],
            'release_time': [],
            'total_time': [],
            'concurrent_requests': [],
            'pool_utilization': [],
            'memory_usage': [],
            'response_time': [],
        }
        self.start_time = None
        self.end_time = None
        
    def start_benchmark(self):
        """Start benchmark timing."""
        self.start_time = time.perf_counter()
        self.metrics = {key: [] for key in self.metrics}
        
    def end_benchmark(self):
        """End benchmark timing."""
        self.end_time = time.perf_counter()
        
    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric."""
        if metric_name in self.metrics:
            self.metrics[metric_name].append(value)
            
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get benchmark statistics."""
        if not self.start_time or not self.end_time:
            return {}
            
        total_duration = self.end_time - self.start_time
        
        stats = {
            'total_duration': total_duration,
            'total_requests': len(self.metrics['total_time']),
            'requests_per_second': len(self.metrics['total_time']) / total_duration if total_duration > 0 else 0,
            'memory_usage_mb': self.get_memory_usage(),
        }
        
        # Add percentile statistics for response times
        for metric_name, values in self.metrics.items():
            if values and metric_name.endswith('_time'):
                sorted_values = sorted(values)
                if sorted_values:
                    stats[f'{metric_name}_p50'] = sorted_values[len(sorted_values) // 2]
                    stats[f'{metric_name}_p95'] = sorted_values[int(len(sorted_values) * 0.95)]
                    stats[f'{metric_name}_p99'] = sorted_values[int(len(sorted_values) * 0.99)]
                    stats[f'{metric_name}_avg'] = sum(values) / len(values)
                    stats[f'{metric_name}_min'] = min(values)
                    stats[f'{metric_name}_max'] = max(values)
                    
        return stats


class TestDatabaseConnectionPoolPerformance:
    """Test database connection pool performance characteristics."""
    
    @pytest_asyncio.fixture
    async def db_pool(self):
        """Create a test database connection pool for performance testing."""
        config = ConnectionPoolConfig(
            pool_name="perf_test_database",
            min_size=5,
            max_size=20,
            timeout=10,
            health_check_interval=30,
        )
        
        # Use SQLite in-memory for performance testing
        database_url = "sqlite:///:memory:"
        
        with patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            
            pool = DatabaseConnectionPool(config, database_url)
            await pool.initialize()
            yield pool
            await pool.shutdown()
            
    @pytest.mark.asyncio
    async def test_database_pool_throughput(self, db_pool):
        """Test database pool throughput under load."""
        benchmark = ConnectionPoolBenchmark()
        benchmark.start_benchmark()
        
        async def database_operation(operation_id: int):
            """Simulate a database operation."""
            start_time = time.perf_counter()
            
            try:
                async with db_pool.get_connection() as engine:
                    # Simulate database work
                    await asyncio.sleep(0.001)  # 1ms simulated work
                    
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    
                    benchmark.record_metric('total_time', total_time)
                    benchmark.record_metric('response_time', total_time)
                    
                    return f"operation_{operation_id}_success"
                    
            except Exception as e:
                benchmark.record_metric('total_time', time.perf_counter() - start_time)
                raise
                
        # Run concurrent operations
        num_operations = 100
        num_concurrent = 10
        
        for batch in range(0, num_operations, num_concurrent):
            batch_size = min(num_concurrent, num_operations - batch)
            tasks = [database_operation(i) for i in range(batch, batch + batch_size)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Record memory usage
            benchmark.record_metric('memory_usage', benchmark.get_memory_usage())
            
        benchmark.end_benchmark()
        
        # Analyze results
        stats = benchmark.get_statistics()
        
        assert stats['total_requests'] >= num_operations * 0.95  # Allow 5% failures
        assert stats['requests_per_second'] > 50  # Should handle at least 50 req/s
        assert stats['response_time_p95'] < 0.1  # 95th percentile under 100ms
        
        print(f"Database Pool Performance:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Requests/second: {stats['requests_per_second']:.2f}")
        print(f"  Response time p95: {stats['response_time_p95']*1000:.2f}ms")
        print(f"  Memory usage: {stats['memory_usage_mb']:.2f}MB")
        
    @pytest.mark.asyncio
    async def test_database_pool_concurrent_stress(self, db_pool):
        """Test database pool under high concurrent stress."""
        results = []
        errors = []
        
        async def stress_operation(operation_id: int):
            """Perform a stressful database operation."""
            try:
                async with db_pool.get_connection() as engine:
                    # Simulate varying workload
                    await asyncio.sleep(0.001 * (operation_id % 5 + 1))
                    results.append(operation_id)
                    return True
            except Exception as e:
                errors.append((operation_id, str(e)))
                return False
                
        # Create high concurrency
        num_tasks = 200
        max_concurrent = 50
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_operation(operation_id: int):
            async with semaphore:
                return await stress_operation(operation_id)
                
        tasks = [limited_operation(i) for i in range(num_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful = sum(1 for r in results if r is True)
        failed = sum(1 for r in results if r is False)
        
        success_rate = successful / num_tasks
        
        assert success_rate > 0.95  # At least 95% success rate
        assert len(errors) < num_tasks * 0.05  # Less than 5% errors
        
        print(f"Database Pool Stress Test:")
        print(f"  Total tasks: {num_tasks}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {success_rate*100:.2f}%")
        
    @pytest.mark.asyncio
    async def test_database_pool_connection_leaks(self, db_pool):
        """Test for database connection leaks."""
        initial_stats = db_pool.get_stats()
        initial_total = initial_stats.total_connections
        
        async def operation_with_potential_leak():
            """Operation that might leak connections."""
            try:
                async with db_pool.get_connection() as engine:
                    await asyncio.sleep(0.01)
                    # Simulate potential exception
                    if asyncio.current_task().get_name() == 'leaky_task':
                        raise Exception("Simulated error")
                    return "success"
            except Exception:
                # Connection should still be released despite exception
                pass
                
        # Run operations
        tasks = [operation_with_potential_leak() for _ in range(50)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Wait for cleanup
        await asyncio.sleep(0.1)
        
        # Check for leaks
        final_stats = db_pool.get_stats()
        final_total = final_stats.total_connections
        
        # Connections should be properly released
        assert final_stats.active_connections == 0
        assert final_total <= initial_total + 10  # Allow small buffer for testing


class TestRedisConnectionPoolPerformance:
    """Test Redis connection pool performance characteristics."""
    
    @pytest_asyncio.fixture
    async def redis_pool(self):
        """Create a test Redis connection pool for performance testing."""
        config = ConnectionPoolConfig(
            pool_name="perf_test_redis",
            min_size=5,
            max_size=20,
            timeout=10,
            retry_attempts=3,
            retry_delay=0.1,
        )
        
        with patch('redis.asyncio.ConnectionPool.from_url') as mock_from_url:
            mock_pool = MagicMock()
            mock_from_url.return_value = mock_pool
            
            pool = RedisConnectionPool(config, "redis://localhost:6379/1")
            await pool.initialize()
            yield pool
            await pool.shutdown()
            
    @pytest.mark.asyncio
    async def test_redis_pool_cache_operations(self, redis_pool):
        """Test Redis pool performance with cache operations."""
        benchmark = ConnectionPoolBenchmark()
        benchmark.start_benchmark()
        
        async def cache_operation(operation_id: int):
            """Simulate cache operation."""
            start_time = time.perf_counter()
            
            try:
                async with redis_pool.get_connection() as client:
                    # Simulate cache operations
                    await asyncio.sleep(0.0005)  # 0.5ms simulated work
                    
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    
                    benchmark.record_metric('total_time', total_time)
                    benchmark.record_metric('response_time', total_time)
                    
                    return f"cache_op_{operation_id}_success"
                    
            except Exception as e:
                benchmark.record_metric('total_time', time.perf_counter() - start_time)
                raise
                
        # Run cache operations
        num_operations = 200
        num_concurrent = 20
        
        for batch in range(0, num_operations, num_concurrent):
            batch_size = min(num_concurrent, num_operations - batch)
            tasks = [cache_operation(i) for i in range(batch, batch + batch_size)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            benchmark.record_metric('memory_usage', benchmark.get_memory_usage())
            
        benchmark.end_benchmark()
        
        stats = benchmark.get_statistics()
        
        assert stats['total_requests'] >= num_operations * 0.95
        assert stats['requests_per_second'] > 100  # Cache should be fast
        assert stats['response_time_p95'] < 0.05  # 95th percentile under 50ms
        
        print(f"Redis Pool Cache Performance:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Requests/second: {stats['requests_per_second']:.2f}")
        print(f"  Response time p95: {stats['response_time_p95']*1000:.2f}ms")
        
    @pytest.mark.asyncio
    async def test_redis_pool_rate_limiting(self, redis_pool):
        """Test Redis pool performance for rate limiting."""
        async def rate_limit_check(client_id: str):
            """Simulate rate limit check."""
            async with redis_pool.get_connection() as client:
                # Simulate rate limit logic
                await asyncio.sleep(0.001)
                return True
                
        # Test rate limiting under load
        num_clients = 100
        concurrent_requests = 10
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def limited_rate_check(client_id: str):
            async with semaphore:
                return await rate_limit_check(client_id)
                
        tasks = [limited_rate_check(f"client_{i}") for i in range(num_clients)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        success_rate = successful / num_clients
        
        assert success_rate > 0.98  # Rate limiting should be very reliable
        

class TestHTTPConnectionPoolPerformance:
    """Test HTTP connection pool performance for external API calls."""
    
    @pytest_asyncio.fixture
    async def http_pool(self):
        """Create a test HTTP connection pool for performance testing."""
        config = ConnectionPoolConfig(
            pool_name="perf_test_http",
            min_size=5,
            max_size=30,
            timeout=15,
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
    async def test_http_pool_api_calls(self, http_pool):
        """Test HTTP pool performance with API calls."""
        benchmark = ConnectionPoolBenchmark()
        benchmark.start_benchmark()
        
        # Mock API responses
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        http_pool._client.get.return_value = mock_response
        
        async def api_call(operation_id: int):
            """Simulate API call."""
            start_time = time.perf_counter()
            
            try:
                async with http_pool.get_connection() as client:
                    # Simulate API call
                    response = await client.get(f"/api/endpoint/{operation_id}")
                    await asyncio.sleep(0.005)  # 5ms network latency
                    
                    end_time = time.perf_counter()
                    total_time = end_time - start_time
                    
                    benchmark.record_metric('total_time', total_time)
                    benchmark.record_metric('response_time', total_time)
                    
                    return response
                    
            except Exception as e:
                benchmark.record_metric('total_time', time.perf_counter() - start_time)
                raise
                
        # Run API calls
        num_operations = 150
        num_concurrent = 15
        
        for batch in range(0, num_operations, num_concurrent):
            batch_size = min(num_concurrent, num_operations - batch)
            tasks = [api_call(i) for i in range(batch, batch + batch_size)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            benchmark.record_metric('memory_usage', benchmark.get_memory_usage())
            
        benchmark.end_benchmark()
        
        stats = benchmark.get_statistics()
        
        assert stats['total_requests'] >= num_operations * 0.95
        assert stats['requests_per_second'] > 50  # External API calls might be slower
        assert stats['response_time_p95'] < 0.2  # 95th percentile under 200ms
        
        print(f"HTTP Pool API Performance:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Requests/second: {stats['requests_per_second']:.2f}")
        print(f"  Response time p95: {stats['response_time_p95']*1000:.2f}ms")
        
    @pytest.mark.asyncio
    async def test_http_pool_circuit_breaker(self, http_pool):
        """Test HTTP pool with circuit breaker behavior."""
        # Simulate failing API
        mock_response = AsyncMock()
        mock_response.status_code = 500
        http_pool._client.get.return_value = mock_response
        
        failure_count = 0
        success_count = 0
        
        async def api_call_with_retry():
            """API call with retry logic."""
            nonlocal failure_count, success_count
            
            for attempt in range(3):  # 3 retry attempts
                try:
                    async with http_pool.get_connection() as client:
                        response = await client.get("/api/test")
                        if response.status_code == 200:
                            success_count += 1
                            return True
                        else:
                            failure_count += 1
                            if attempt < 2:
                                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                            
                except Exception:
                    failure_count += 1
                    
            return False
            
        # Test with circuit breaker
        tasks = [api_call_with_retry() for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should handle failures gracefully
        assert failure_count > 0  # Some failures expected
        

class TestWebSocketConnectionPoolPerformance:
    """Test WebSocket connection pool performance."""
    
    @pytest_asyncio.fixture
    async def ws_manager(self):
        """Create a test WebSocket pool manager."""
        manager = WebSocketPoolManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()
        
    @pytest.mark.asyncio
    async def test_websocket_concurrent_connections(self, ws_manager):
        """Test WebSocket concurrent connection handling."""
        benchmark = ConnectionPoolBenchmark()
        benchmark.start_benchmark()
        
        async def websocket_session(client_id: str):
            """Simulate WebSocket session."""
            start_time = time.perf_counter()
            
            try:
                # Create mock WebSocket
                mock_websocket = AsyncMock()
                mock_websocket.client_state.DISCONNECTED = False
                
                # Connect
                await ws_manager.connect(mock_websocket, client_id)
                
                # Simulate some activity
                await asyncio.sleep(0.01)
                
                # Send message
                await ws_manager.send_personal_message(f"Hello {client_id}", client_id)
                
                # Disconnect
                await ws_manager.disconnect(client_id)
                
                end_time = time.perf_counter()
                total_time = end_time - start_time
                
                benchmark.record_metric('total_time', total_time)
                benchmark.record_metric('response_time', total_time)
                
                return f"ws_session_{client_id}_success"
                
            except Exception as e:
                benchmark.record_metric('total_time', time.perf_counter() - start_time)
                raise
                
        # Run concurrent WebSocket sessions
        num_sessions = 100
        concurrent_sessions = 10
        
        for batch in range(0, num_sessions, concurrent_sessions):
            batch_size = min(concurrent