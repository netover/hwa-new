"""
Redis connection pool implementation for the Resync project.
Separated to follow Single Responsibility Principle.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import redis.asyncio as redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError

from resync.core.exceptions import DatabaseError
from resync.core.pools.base_pool import ConnectionPool, ConnectionPoolConfig

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class RedisConnectionPool(ConnectionPool[AsyncRedis]):
    """Redis connection pool with advanced features."""

    def __init__(self, config: ConnectionPoolConfig, redis_url: str):
        super().__init__(config)
        self.redis_url = redis_url
        self._connection_pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[AsyncRedis] = None

    async def _setup_pool(self) -> None:
        """Setup Redis connection pool."""
        try:
            # Setup Redis connection pool with optimized settings
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.max_size,
                min_connections=self.config.min_size,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=self.config.health_check_interval,
                retry_on_timeout=True,
            )
            
            # Create Redis client with the connection pool
            self._client = redis.Redis(
                connection_pool=self._connection_pool,
                socket_connect_timeout=self.config.connection_timeout,
                socket_timeout=self.config.connection_timeout,
                health_check_interval=self.config.health_check_interval
            )

            # Test the connection
            await self._client.ping()

            logger.info(f"Redis connection pool '{self.config.pool_name}' initialized with {self.config.min_size}-{self.config.max_size} connections")
        except Exception as e:
            logger.error(f"Failed to setup Redis connection pool: {e}")
            raise DatabaseError(f"Failed to setup Redis connection pool: {e}") from e

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[AsyncRedis]:
        """Get a Redis connection from the pool."""
        if not self._initialized or self._shutdown:
            raise DatabaseError("Redis pool not initialized or shutdown")

        if not self._client:
            raise DatabaseError("Redis client not available")

        start_time = time.time()

        try:
            # Record pool request
            await self.increment_stat('pool_hits')

            # Yield the Redis client (connection pooling is handled internally by Redis-py)
            yield self._client

        except RedisConnectionError as e:
            await self.increment_stat('connection_errors')
            await self.increment_stat('pool_misses')
            logger.error(f"Redis connection error: {e}")
            raise DatabaseError(f"Redis connection error: {e}") from e
        except RedisError as e:
            await self.increment_stat('pool_misses')
            logger.error(f"Redis error: {e}")
            raise DatabaseError(f"Redis error: {e}") from e
        except Exception as e:
            await self.increment_stat('pool_misses')
            logger.error(f"Failed to get Redis connection: {e}")
            raise DatabaseError(f"Failed to acquire Redis connection: {e}") from e
        finally:
            wait_time = time.time() - start_time
            await self.update_wait_time(wait_time)

            # Record connection metrics
            logger.debug(f"Redis connection acquired in {wait_time:.3f}s for pool {self.config.pool_name}")

    async def _close_pool(self) -> None:
        """Close the Redis connection pool."""
        if self._client:
            await self._client.aclose(close_connection_pool=True)
            logger.info(f"Redis connection pool '{self.config.pool_name}' closed")