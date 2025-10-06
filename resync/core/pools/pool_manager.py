"""
Connection pool manager implementation for the Resync project.
Separated to follow Single Responsibility Principle.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional, TYPE_CHECKING

from resync.core.exceptions import TWSConnectionError
from resync.core.pools.base_pool import ConnectionPool
from resync.core.pools.db_pool import DatabaseConnectionPool
from resync.core.pools.redis_pool import RedisConnectionPool
from resync.core.pools.http_pool import HTTPConnectionPool
from resync.core.pools.base_pool import ConnectionPoolConfig
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    import redis.asyncio as redis
    import httpx


async def get_connection_pool_manager() -> ConnectionPoolManager:
    """
    Factory function to get the connection pool manager instance.
    This ensures the manager is properly initialized before use.
    """
    if not hasattr(get_connection_pool_manager, '_instance'):
        get_connection_pool_manager._instance = ConnectionPoolManager()
        await get_connection_pool_manager._instance.initialize()
    
    return get_connection_pool_manager._instance


class ConnectionPoolManager:
    """Central manager for all connection pools."""

    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self._initialized = False
        self._shutdown = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize all connection pools."""
        if self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                # Initialize database connection pool
                if settings.DB_POOL_MIN_SIZE > 0:
                    db_config = ConnectionPoolConfig(
                        pool_name="database",
                        min_size=settings.DB_POOL_MIN_SIZE,
                        max_size=settings.DB_POOL_MAX_SIZE,
                        idle_timeout=settings.DB_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.DB_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.DB_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.DB_POOL_MAX_LIFETIME
                    )
                    db_pool = DatabaseConnectionPool(db_config, settings.DATABASE_URL)
                    await db_pool.initialize()
                    self.pools["database"] = db_pool

                # Initialize Redis connection pool
                if settings.REDIS_POOL_MIN_SIZE > 0:
                    redis_config = ConnectionPoolConfig(
                        pool_name="redis",
                        min_size=settings.REDIS_POOL_MIN_SIZE,
                        max_size=settings.REDIS_POOL_MAX_SIZE,
                        idle_timeout=settings.REDIS_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.REDIS_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.REDIS_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.REDIS_POOL_MAX_LIFETIME
                    )
                    redis_pool = RedisConnectionPool(redis_config, settings.REDIS_URL)
                    await redis_pool.initialize()
                    self.pools["redis"] = redis_pool

                # Initialize HTTP connection pool for TWS
                if settings.HTTP_POOL_MIN_SIZE > 0:
                    http_config = ConnectionPoolConfig(
                        pool_name="tws_http",
                        min_size=settings.HTTP_POOL_MIN_SIZE,
                        max_size=settings.HTTP_POOL_MAX_SIZE,
                        idle_timeout=settings.HTTP_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.HTTP_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.HTTP_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.HTTP_POOL_MAX_LIFETIME
                    )
                    http_pool = HTTPConnectionPool(http_config, settings.TWS_BASE_URL)
                    await http_pool.initialize()
                    self.pools["tws_http"] = http_pool

                self._initialized = True
                logger.info("Connection pool manager initialized with %d pools", len(self.pools))
            except Exception as e:
                logger.error("Failed to initialize connection pool manager: %s", e)
                raise TWSConnectionError(f"Failed to initialize connection pool manager: {e}") from e

    async def get_pool(self, pool_name: str) -> Optional[ConnectionPool]:
        """Get a specific connection pool by name."""
        return self.pools.get(pool_name)

    def get_pool_stats(self):
        """Get statistics for all pools."""
        stats = {}
        for name, pool in self.pools.items():
            stats[name] = pool.stats
        return stats

    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all pools."""
        results = {}
        for name, pool in self.pools.items():
            try:
                results[name] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for pool {name}: {e}")
                results[name] = False
        return results

    async def close_all(self) -> None:
        """Close all connection pools."""
        if not self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._shutdown:
                return

            for name, pool in self.pools.items():
                try:
                    await pool.close()
                except Exception as e:
                    logger.error(f"Error closing {name} pool: {e}")

            self._shutdown = True
            logger.info("All connection pools closed")
"""
Connection pool manager implementation for the Resync project.
Separated to follow Single Responsibility Principle.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional, TYPE_CHECKING, Any, List

from resync.core.exceptions import TWSConnectionError
from resync.core.pools.base_pool import ConnectionPool
from resync.core.pools.db_pool import DatabaseConnectionPool
from resync.core.pools.redis_pool import RedisConnectionPool
from resync.core.pools.http_pool import HTTPConnectionPool
from resync.core.pools.base_pool import ConnectionPoolConfig
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine
    import redis.asyncio as redis
    import httpx


async def get_connection_pool_manager() -> ConnectionPoolManager:
    """
    Factory function to get the connection pool manager instance.
    This ensures the manager is properly initialized before use.
    """
    if not hasattr(get_connection_pool_manager, '_instance'):
        get_connection_pool_manager._instance = ConnectionPoolManager()
        await get_connection_pool_manager._instance.initialize()
    
    return get_connection_pool_manager._instance


class ConnectionPoolManager:
    """
    Central manager for all connection pools with performance optimization.
    
    Features:
    - Centralized pool management
    - Performance monitoring and optimization
    - Health checking
    - Auto-tuning recommendations
    """

    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self._initialized = False
        self._shutdown = False
        self._lock = asyncio.Lock()
        self._pool_optimizers: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize all connection pools with performance monitoring."""
        if self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                # Import performance optimizer here to avoid circular imports
                from resync.core.performance_optimizer import get_performance_service
                performance_service = get_performance_service()
                
                # Initialize database connection pool
                if settings.DB_POOL_MIN_SIZE > 0:
                    db_config = ConnectionPoolConfig(
                        pool_name="database",
                        min_size=settings.DB_POOL_MIN_SIZE,
                        max_size=settings.DB_POOL_MAX_SIZE,
                        idle_timeout=settings.DB_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.DB_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.DB_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.DB_POOL_MAX_LIFETIME
                    )
                    db_pool = DatabaseConnectionPool(db_config, settings.DATABASE_URL)
                    await db_pool.initialize()
                    self.pools["database"] = db_pool
                    
                    # Register pool for optimization
                    self._pool_optimizers["database"] = await performance_service.register_pool("database")

                # Initialize Redis connection pool
                if settings.REDIS_POOL_MIN_SIZE > 0:
                    redis_config = ConnectionPoolConfig(
                        pool_name="redis",
                        min_size=settings.REDIS_POOL_MIN_SIZE,
                        max_size=settings.REDIS_POOL_MAX_SIZE,
                        idle_timeout=settings.REDIS_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.REDIS_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.REDIS_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.REDIS_POOL_MAX_LIFETIME
                    )
                    redis_pool = RedisConnectionPool(redis_config, settings.REDIS_URL)
                    await redis_pool.initialize()
                    self.pools["redis"] = redis_pool
                    
                    # Register pool for optimization
                    self._pool_optimizers["redis"] = await performance_service.register_pool("redis")

                # Initialize HTTP connection pool for TWS
                if settings.HTTP_POOL_MIN_SIZE > 0:
                    http_config = ConnectionPoolConfig(
                        pool_name="tws_http",
                        min_size=settings.HTTP_POOL_MIN_SIZE,
                        max_size=settings.HTTP_POOL_MAX_SIZE,
                        idle_timeout=settings.HTTP_POOL_IDLE_TIMEOUT,
                        connection_timeout=settings.HTTP_POOL_CONNECT_TIMEOUT,
                        health_check_interval=settings.HTTP_POOL_HEALTH_CHECK_INTERVAL,
                        max_lifetime=settings.HTTP_POOL_MAX_LIFETIME
                    )
                    http_pool = HTTPConnectionPool(http_config, settings.TWS_BASE_URL)
                    await http_pool.initialize()
                    self.pools["tws_http"] = http_pool
                    
                    # Register pool for optimization
                    self._pool_optimizers["tws_http"] = await performance_service.register_pool("tws_http")

                self._initialized = True
                logger.info("Connection pool manager initialized with %d pools", len(self.pools))
            except Exception as e:
                logger.error("Failed to initialize connection pool manager: %s", e)
                raise TWSConnectionError(f"Failed to initialize connection pool manager: {e}") from e

    async def get_pool(self, pool_name: str) -> Optional[ConnectionPool]:
        """Get a specific connection pool by name."""
        return self.pools.get(pool_name)

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools."""
        stats = {}
        for name, pool in self.pools.items():
            stats[name] = {
                "active_connections": pool.stats.active_connections,
                "idle_connections": pool.stats.idle_connections,
                "total_connections": pool.stats.total_connections,
                "waiting_connections": pool.stats.waiting_connections,
                "connection_errors": pool.stats.connection_errors,
                "pool_hits": pool.stats.pool_hits,
                "pool_misses": pool.stats.pool_misses,
                "pool_exhaustions": pool.stats.pool_exhaustions,
                "average_wait_time": pool.stats.average_wait_time,
                "peak_connections": pool.stats.peak_connections,
            }
        return stats

    async def get_optimization_recommendations(self) -> Dict[str, List[str]]:
        """
        Get optimization recommendations for all connection pools.
        
        Returns:
            Dictionary mapping pool names to lists of recommendations
        """
        recommendations = {}
        
        for pool_name, optimizer in self._pool_optimizers.items():
            if pool_name in self.pools:
                pool = self.pools[pool_name]
                pool_stats = {
                    "active_connections": pool.stats.active_connections,
                    "idle_connections": pool.stats.idle_connections,
                    "total_connections": pool.stats.total_connections,
                    "waiting_connections": pool.stats.waiting_connections,
                    "connection_errors": pool.stats.connection_errors,
                    "pool_hits": pool.stats.pool_hits,
                    "pool_misses": pool.stats.pool_misses,
                    "pool_exhaustions": pool.stats.pool_exhaustions,
                    "average_wait_time": pool.stats.average_wait_time,
                    "peak_connections": pool.stats.peak_connections,
                }
                
                metrics = await optimizer.get_current_metrics(pool_stats)
                recommendations[pool_name] = await optimizer.get_optimization_recommendations(metrics)
        
        return recommendations

    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all pools."""
        results = {}
        for name, pool in self.pools.items():
            try:
                results[name] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for pool {name}: {e}")
                results[name] = False
        return results

    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report for all connection pools.
        
        Returns:
            Dictionary containing metrics and recommendations for all pools
        """
        report = {
            "timestamp": asyncio.get_event_loop().time(),
            "pools": {},
        }
        
        for pool_name, pool in self.pools.items():
            pool_stats = {
                "active_connections": pool.stats.active_connections,
                "idle_connections": pool.stats.idle_connections,
                "total_connections": pool.stats.total_connections,
                "waiting_connections": pool.stats.waiting_connections,
                "connection_errors": pool.stats.connection_errors,
                "pool_hits": pool.stats.pool_hits,
                "pool_misses": pool.stats.pool_misses,
                "pool_exhaustions": pool.stats.pool_exhaustions,
                "average_wait_time": pool.stats.average_wait_time,
                "peak_connections": pool.stats.peak_connections,
            }
            
            # Get optimizer recommendations if available
            recommendations = []
            if pool_name in self._pool_optimizers:
                optimizer = self._pool_optimizers[pool_name]
                metrics = await optimizer.get_current_metrics(pool_stats)
                recommendations = await optimizer.get_optimization_recommendations(metrics)
                
                utilization = metrics.calculate_utilization()
                efficiency_score = metrics.calculate_efficiency_score()
            else:
                utilization = 0.0
                efficiency_score = 0.0
            
            report["pools"][pool_name] = {
                "stats": pool_stats,
                "utilization": f"{utilization:.1f}%",
                "efficiency_score": f"{efficiency_score:.1f}/100",
                "recommendations": recommendations,
            }
        
        return report

    async def close_all(self) -> None:
        """Close all connection pools."""
        if not self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._shutdown:
                return

            for name, pool in self.pools.items():
                try:
                    await pool.close()
                except Exception as e:
                    logger.error(f"Error closing {name} pool: {e}")

            self._shutdown = True
            logger.info("All connection pools closed")
