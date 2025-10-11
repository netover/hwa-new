import asyncio
import logging
import os
import random
import socket
import sys
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    BusyLoadingError,
    RedisError,
)

from resync.settings import settings

logger = logging.getLogger(__name__)


class RedisInitializer:
    """
    Thread-safe Redis initialization with connection pooling.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self._initialized = False
        self._client: Optional[redis.Redis] = None

    async def initialize(
        self,
        max_retries: int = 3,
        base_backoff: float = 0.1,
        max_backoff: float = 10.0,
        health_check_interval: int = 5,
    ) -> redis.Redis:
        """
        Initialize Redis with:
        - Lock para evitar inicialização concorrente
        - Health check contínuo
        - Connection pooling adequado
        - Distributed lock para múltiplas instâncias
        """
        async with self._lock:
            if self._initialized and self._client:
                # Verify connection is still alive
                try:
                    await asyncio.wait_for(self._client.ping(), timeout=1.0)
                    return self._client
                except (RedisError, asyncio.TimeoutError):
                    logger.warning("Existing Redis connection lost, reinitializing")
                    self._initialized = False

            # Distributed lock para evitar thundering herd
            lock_key = "resync:init:lock"
            lock_timeout = 30  # 30 seconds

            for attempt in range(max_retries):
                try:
                    redis_client = await self._create_client_with_pool()

                    # Acquire distributed lock
                    acquired = await redis_client.set(
                        lock_key, f"instance-{os.getpid()}", nx=True, ex=lock_timeout
                    )

                    if not acquired:
                        logger.info(
                            f"Another instance is initializing Redis, "
                            f"waiting... (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(2)
                        continue

                    try:
                        # Validate connection with timeout
                        await asyncio.wait_for(redis_client.ping(), timeout=2.0)

                        # Test write/read operations
                        test_key = f"resync:health:test:{os.getpid()}"
                        await redis_client.set(test_key, "ok", ex=60)
                        test_value = await redis_client.get(test_key)

                        if test_value != b"ok":
                            raise ValueError("Redis read/write test failed")

                        await redis_client.delete(test_key)

                        # Initialize idempotency manager atomically
                        idempotency_manager = await self._initialize_idempotency(
                            redis_client
                        )

                        self._client = redis_client
                        self._initialized = True

                        logger.info(
                            "Redis and idempotency manager initialized successfully",
                            extra={
                                "attempt": attempt + 1,
                                "pool_size": redis_client.connection_pool.max_connections,
                            },
                        )

                        # Start background health check
                        asyncio.create_task(
                            self._health_check_loop(health_check_interval)
                        )

                        return redis_client

                    finally:
                        # Release distributed lock
                        await redis_client.delete(lock_key)

                except (ConnectionError, TimeoutError, BusyLoadingError) as e:
                    if attempt >= max_retries - 1:
                        logger.critical(
                            f"CRITICAL: Redis initialization failed after "
                            f"{max_retries} attempts",
                            exc_info=True,
                        )
                        sys.exit(1)

                    backoff = min(max_backoff, base_backoff * (2**attempt))
                    jitter = random.uniform(0, 0.1 * backoff)  # Add jitter
                    total_wait = backoff + jitter

                    logger.warning(
                        f"Redis connection failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {total_wait:.2f}s"
                    )
                    await asyncio.sleep(total_wait)

                except AuthenticationError as e:
                    logger.critical(f"CRITICAL: Redis authentication failed: {e}")
                    sys.exit(1)

                except Exception as e:
                    logger.critical(
                        "CRITICAL: Unexpected error during Redis initialization",
                        exc_info=True,
                    )
                    sys.exit(1)

        raise RuntimeError("Redis initialization failed - should not reach here")

    async def _create_client_with_pool(self) -> redis.Redis:
        """Create Redis client with optimized connection pool."""
        return redis.Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            socket_connect_timeout=5,
            socket_keepalive=True,
            socket_keepalive_options={
                socket.TCP_KEEPIDLE: 60,
                socket.TCP_KEEPINTVL: 10,
                socket.TCP_KEEPCNT: 3,
            },
            health_check_interval=30,
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
        )

    async def _initialize_idempotency(self, redis_client: redis.Redis):
        """Initialize idempotency manager atomically."""
        from resync.core.container import app_container
        from resync.core.idempotency import IdempotencyManager

        # Ensure idempotency manager gets the validated client
        idempotency_manager = IdempotencyManager(redis_client)
        app_container.register_instance(IdempotencyManager, idempotency_manager)

        return idempotency_manager

    async def _health_check_loop(self, interval: int):
        """Background health check to detect connection issues."""
        while self._initialized:
            try:
                await asyncio.sleep(interval)

                if self._client:
                    await asyncio.wait_for(self._client.ping(), timeout=2.0)

            except (RedisError, asyncio.TimeoutError) as e:
                logger.error(
                    "Redis health check failed - connection may be lost", exc_info=True
                )
                self._initialized = False
                # Trigger alert/metric

            except Exception as e:
                logger.error("Unexpected error in Redis health check", exc_info=True)

    async def close(self):
        """Close Redis connection and cleanup resources."""
        if self._client:
            await self._client.close()
            await self._client.connection_pool.disconnect()
