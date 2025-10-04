
from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

import httpx
import redis.asyncio as redis
from redis.asyncio import Redis as AsyncRedis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, StaticPool

from resync.core.exceptions import DatabaseError, TWSConnectionError
from resync.core.metrics import runtime_metrics
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- Type Definitions ---
T = TypeVar('T')

@dataclass
class ConnectionPoolStats:
    """Statistics for connection pool monitoring."""
    pool_name: str
    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    waiting_connections: int = 0
    connection_errors: int = 0
    connection_creations: int = 0
    connection_closures: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    pool_exhaustions: int = 0
    last_health_check: Optional[datetime] = None
    average_wait_time: float = 0.0
    peak_connections: int = 0

@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools."""
    pool_name: str
    min_size: int = 5
    max_size: int = 20
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    health_check_interval: int = 60
    idle_timeout: int = 300
    enabled: bool = True

class ConnectionPool(ABC, Generic[T]):
    """Abstract base class for connection pools."""

    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.stats = ConnectionPoolStats(pool_name=config.pool_name)
        self._pool: Optional[Any] = None
        self._initialized = False
        self._shutdown = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._wait_times: List[float] = []

    @abstractmethod
    async def _create_connection(self) -> T:
        """Create a new connection."""
        pass

    @abstractmethod
    async def _validate_connection(self, connection: T) -> bool:
        """Validate that a connection is still usable."""
        pass

    @abstractmethod
    async def _close_connection(self, connection: T) -> None:
        """Close a connection."""
        pass

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._initialized:
                return

            try:
                await self._setup_pool()
                self._initialized = True
                self._health_check_task = asyncio.create_task(self._health_check_loop())
                logger.info(f"Connection pool '{self.config.pool_name}' initialized")

                # Record initialization metric
                runtime_metrics.record_gauge(
                    f"connection_pool.{self.config.pool_name}.initialized",
                    1,
                    {"pool_name": self.config.pool_name}
                )
            except Exception as e:
                logger.error(f"Failed to initialize connection pool '{self.config.pool_name}': {e}")
                raise

    async def _setup_pool(self) -> None:
        """Setup the underlying connection pool implementation."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the connection pool and cleanup resources."""
        if self._shutdown:
            return

        self._shutdown = True

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        await self._cleanup_pool()
        self._initialized = False
        logger.info(f"Connection pool '{self.config.pool_name}' shutdown")

        # Record shutdown metric
        runtime_metrics.record_gauge(
            f"connection_pool.{self.config.pool_name}.initialized",
            0,
            {"pool_name": self.config.pool_name}
        )

    async def _cleanup_pool(self) -> None:
        """Cleanup the underlying connection pool implementation."""
        pass

    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while not self._shutdown:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self.health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check failed for pool '{self.config.pool_name}': {e}")

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check on the connection pool."""
        pass

    def get_stats(self) -> ConnectionPoolStats:
        """Get current pool statistics."""
        return self.stats

    def update_wait_time(self, wait_time: float) -> None:
        """Update average wait time statistics."""
        self._wait_times.append(wait_time)
        if len(self._wait_times) > 100:  # Keep last 100 measurements
            self._wait_times.pop(0)
        self.stats.average_wait_time = sum(self._wait_times) / len(self._wait_times)

class DatabaseConnectionPool(ConnectionPool[Engine]):
    """Database connection pool supporting PostgreSQL, MySQL, and SQLite."""

    def __init__(self, config: ConnectionPoolConfig, database_url: str):
        super().__init__(config)
        self.database_url = database_url
        self._engine: Optional[Engine] = None  # For backward compatibility
        self._async_engine = None
        self._async_sessionmaker = None

    async def _setup_pool(self) -> None:
        """Setup SQLAlchemy async connection pool."""
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            from sqlalchemy.pool import QueuePool, StaticPool
            
            # Configure pool based on database type with enhanced settings
            if self.database_url.startswith("sqlite"):
                # SQLite uses StaticPool for single connections
                pool_kwargs = {
                    "poolclass": StaticPool,
                    "pool_size": 1,
                    "max_overflow": 0,
                    "pool_pre_ping": True,
                    "pool_recycle": self.config.idle_timeout,
                    # Memory optimization settings
                    "pool_logging_name": f"{self.config.pool_name}_db_pool",
                    "echo": False,
                }
            else:
                # PostgreSQL/MySQL use QueuePool with optimized settings
                pool_kwargs = {
                    "poolclass": QueuePool,
                    "pool_size": max(20, self.config.min_size),  # Enhanced default
                    "max_overflow": max(50, self.config.max_size - self.config.min_size),  # Enhanced default
                    "pool_timeout": self.config.timeout,
                    "pool_recycle": self.config.idle_timeout,
                    "pool_pre_ping": True,  # Validate connections before use
                    "pool_reset_on_return": "commit",
                    "echo": False,  # Set to True for debugging only
                    # Memory and performance optimizations
                    "pool_logging_name": f"{self.config.pool_name}_db_pool",
                    "pool_use_lifo": True,  # Use LIFO to keep hot connections
                    "pool_pre_reset": True,
                    "pool_post_reset": True,
                }
                
                # Add SSL configuration for production if PostgreSQL
                if "postgresql" in self.database_url:
                    pool_kwargs["connect_args"] = {"ssl": "require"}

            # Create async engine with optimized settings
            self._async_engine = create_async_engine(
                self.database_url,
                **pool_kwargs,
                # Additional engine-level optimizations
                future=True,
                pool_pre_ping=True,
                pool_recycle=self.config.idle_timeout,
                pool_logging_name=f"{self.config.pool_name}_engine"
            )
            
            # Create sessionmaker for async sessions
            self._async_sessionmaker = async_sessionmaker(
                self._async_engine, 
                expire_on_commit=False,
                class_=None,
                sync_session_class=None
            )

            # Test connection
            await self.health_check()

        except Exception as e:
            logger.error(f"Failed to setup database connection pool: {e}")
            raise

    async def _create_connection(self):
        """Return the SQLAlchemy async engine as the connection."""
        if not self._async_engine:
            raise DatabaseError("Database engine not initialized")
        return self._async_engine

    async def _validate_connection(self, connection):
        """Validate database connection."""
        try:
            from sqlalchemy import text
            # Use a simple async query to test connection
            async with connection.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return result.scalar() == 1
        except SQLAlchemyError:
            return False

    async def _close_connection(self, connection: Engine) -> None:
        """Close database connection (handled by SQLAlchemy pool)."""
        pass  # SQLAlchemy handles connection lifecycle

    async def _cleanup_pool(self) -> None:
        """Cleanup SQLAlchemy async engine."""
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None

    async def health_check(self) -> bool:
        """Perform database health check."""
        if not self._async_engine:
            return False

        try:
            start_time = time.time()
            is_healthy = await self._validate_connection(self._async_engine)
            check_time = time.time() - start_time

            # For async engines, we can't access pool stats the same way
            # Using a different approach for metrics
            self.stats.last_health_check = datetime.now()

            # Record health check metrics
            runtime_metrics.record_gauge(
                f"connection_pool.{self.config.pool_name}.healthy",
                1 if is_healthy else 0,
                {"pool_name": self.config.pool_name}
            )
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.health_check_duration",
                check_time,
                {"pool_name": self.config.pool_name}
            )

            return is_healthy

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            self.stats.connection_errors += 1
            return False

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self._initialized or self._shutdown:
            raise DatabaseError("Database pool not initialized or shutdown")

        start_time = time.time()
        wait_time = 0.0

        try:
            # Record pool request
            self.stats.pool_hits += 1

            # Get async session from sessionmaker
            async with self._async_sessionmaker() as session:
                try:
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        except Exception as e:
            self.stats.pool_misses += 1
            logger.error(f"Failed to get database connection: {e}")
            raise DatabaseError(f"Failed to acquire database connection: {e}") from e
        finally:
            wait_time = time.time() - start_time
            self.update_wait_time(wait_time)

            # Record connection metrics
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.acquire_time",
                wait_time,
                {"pool_name": self.config.pool_name}
            )

class RedisConnectionPool(ConnectionPool[AsyncRedis]):
    """Redis connection pool with advanced features."""

    def __init__(self, config: ConnectionPoolConfig, redis_url: str):
        super().__init__(config)
        self.redis_url = redis_url
        self._connection_pool: Optional[redis.ConnectionPool] = None

    async def _setup_pool(self) -> None:
        """Setup Redis connection pool."""
        try:
            # Setup Redis connection pool with optimized settings
            self._connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.max_size,
                min_connections=max(1, self.config.min_size // 2),  # Keep some minimum connections
                socket_connect_timeout=self.config.timeout,
                socket_timeout=self.config.timeout,
                health_check_interval=self.config.health_check_interval,
                retry_on_timeout=True,
                retry_on_error=[RedisConnectionError],
                retry=redis.Retry(
                    backoff=redis.ExponentialBackoff(
                        cap=self.config.retry_delay * 10,
                        base=self.config.retry_delay
                    ),
                    retries=self.config.retry_attempts
                ),
                # Additional optimizations for memory and resource management
                max_idle_time=self.config.idle_timeout,
                idle_check_interval=30
            )

            # Test connection
            await self.health_check()

        except Exception as e:
            logger.error(f"Failed to setup Redis connection pool: {e}")
            raise

    async def _create_connection(self) -> AsyncRedis:
        """Create Redis connection from pool."""
        if not self._connection_pool:
            raise RedisError("Redis connection pool not initialized")
        return AsyncRedis(connection_pool=self._connection_pool)

    async def _validate_connection(self, connection: AsyncRedis) -> bool:
        """Validate Redis connection."""
        try:
            await connection.ping()
            return True
        except RedisError:
            return False

    async def _close_connection(self, connection: AsyncRedis) -> None:
        """Close Redis connection."""
        if connection:
            await connection.close()

    async def _cleanup_pool(self) -> None:
        """Cleanup Redis connection pool."""
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None

    async def health_check(self) -> bool:
        """Perform Redis health check."""
        if not self._connection_pool:
            return False

        try:
            start_time = time.time()
            connection = await self._create_connection()
            is_healthy = await self._validate_connection(connection)
            await self._close_connection(connection)
            check_time = time.time() - start_time

            self.stats.last_health_check = datetime.now()
            self.stats.total_connections = len(self._connection_pool._connections)
            self.stats.active_connections = len([
                conn for conn in self._connection_pool._connections
                if conn.is_connected
            ])
            self.stats.idle_connections = self.stats.total_connections - self.stats.active_connections

            # Record health check metrics
            runtime_metrics.record_gauge(
                f"connection_pool.{self.config.pool_name}.healthy",
                1 if is_healthy else 0,
                {"pool_name": self.config.pool_name}
            )
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.health_check_duration",
                check_time,
                {"pool_name": self.config.pool_name}
            )

            return is_healthy

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self.stats.connection_errors += 1
            return False

    @asynccontextmanager
    async def get_connection(self):
        """Get a Redis connection from the pool."""
        if not self._initialized or self._shutdown:
            raise RedisError("Redis pool not initialized or shutdown")

        start_time = time.time()
        connection = None

        try:
            # Record pool request
            self.stats.pool_hits += 1

            # Get connection from pool
            connection = await self._create_connection()
            yield connection

        except Exception as e:
            self.stats.pool_misses += 1
            logger.error(f"Failed to get Redis connection: {e}")
            raise RedisError(f"Failed to acquire Redis connection: {e}") from e
        finally:
            wait_time = time.time() - start_time
            self.update_wait_time(wait_time)

            if connection:
                await self._close_connection(connection)

            # Record connection metrics
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.acquire_time",
                wait_time,
                {"pool_name": self.config.pool_name}
            )

class HTTPConnectionPool(ConnectionPool[httpx.AsyncClient]):
    """HTTP connection pool for external API calls."""

    def __init__(self, config: ConnectionPoolConfig, base_url: str, **client_kwargs):
        super().__init__(config)
        self.base_url = base_url
        self.client_kwargs = client_kwargs
        self._client: Optional[httpx.AsyncClient] = None

    async def _setup_pool(self) -> None:
        """Setup HTTP connection pool using httpx."""
        try:
            # Configure httpx client with connection pooling
            limits = httpx.Limits(
                max_connections=self.config.max_size,
                max_keepalive_connections=max(self.config.min_size, 10),
                keepalive_expiry=self.config.idle_timeout,
                # Additional limits for memory management
                max_keepalive_per_pool=max(self.config.min_size // 2, 5)
            )

            timeout = httpx.Timeout(
                connect=settings.TWS_CONNECT_TIMEOUT,
                read=settings.TWS_READ_TIMEOUT,
                write=settings.TWS_WRITE_TIMEOUT,
                pool=settings.TWS_POOL_TIMEOUT,
            )

            # Configure transport for optimized memory usage
            transport = httpx.AsyncHTTPTransport(
                pool_limits=limits,
                # Additional optimizations
                retries=self.config.retry_attempts,
                verify_ssl=False,  # This matches the existing TWS setup
            )

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                limits=limits,
                timeout=timeout,
                transport=transport,  # Use optimized transport
                **self.client_kwargs
            )

            # Test connection
            await self.health_check()

        except Exception as e:
            logger.error(f"Failed to setup HTTP connection pool: {e}")
            raise

    async def _create_connection(self) -> httpx.AsyncClient:
        """Return the httpx client as the connection."""
        if not self._client:
            raise TWSConnectionError("HTTP client not initialized")
        return self._client

    async def _validate_connection(self, connection: httpx.AsyncClient) -> bool:
        """Validate HTTP connection."""
        try:
            # Use a simple HEAD request to test connectivity
            response = await connection.head("", timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False

    async def _close_connection(self, connection: httpx.AsyncClient) -> None:
        """Close HTTP connection (handled by httpx)."""
        pass  # httpx handles connection lifecycle

    async def _cleanup_pool(self) -> None:
        """Cleanup httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Perform HTTP health check."""
        if not self._client:
            return False

        try:
            start_time = time.time()
            is_healthy = await self._validate_connection(self._client)
            check_time = time.time() - start_time

            self.stats.last_health_check = datetime.now()

            # Record health check metrics
            runtime_metrics.record_gauge(
                f"connection_pool.{self.config.pool_name}.healthy",
                1 if is_healthy else 0,
                {"pool_name": self.config.pool_name}
            )
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.health_check_duration",
                check_time,
                {"pool_name": self.config.pool_name}
            )

            return is_healthy

        except Exception as e:
            logger.error(f"HTTP health check failed: {e}")
            self.stats.connection_errors += 1
            return False

    @asynccontextmanager
    async def get_connection(self):
        """Get an HTTP connection from the pool."""
        if not self._initialized or self._shutdown:
            raise TWSConnectionError("HTTP pool not initialized or shutdown")

        start_time = time.time()

        try:
            # Record pool request
            self.stats.pool_hits += 1

            # Get connection (httpx handles pooling)
            client = await self._create_connection()
            yield client

        except Exception as e:
            self.stats.pool_misses += 1
            logger.error(f"Failed to get HTTP connection: {e}")
            raise TWSConnectionError(f"Failed to acquire HTTP connection: {e}") from e
        finally:
            wait_time = time.time() - start_time
            self.update_wait_time(wait_time)

            # Record connection metrics
            runtime_metrics.record_histogram(
                f"connection_pool.{self.config.pool_name}.acquire_time",
                wait_time,
                {"pool_name": self.config.pool_name}
            )

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
                        timeout=settings.DB_POOL_TIMEOUT,
                        retry_attempts=settings.DB_POOL_RETRY_ATTEMPTS,
                        retry_delay=settings.DB_POOL_RETRY_DELAY,
                        health_check_interval=settings.DB_POOL_HEALTH_CHECK_INTERVAL,
                        idle_timeout=settings.DB_POOL_IDLE_TIMEOUT,
                    )
                    # Use SQLite for now, can be extended to PostgreSQL/MySQL
                    database_url = f"sqlite:///{settings.BASE_DIR}/audit_queue.db"
                    self.pools["database"] = DatabaseConnectionPool(db_config, database_url)

                # Initialize Redis connection pool
                if settings.REDIS_POOL_MIN_SIZE > 0:
                    redis_config = ConnectionPoolConfig(
                        pool_name="redis",
                        min_size=settings.REDIS_POOL_MIN_SIZE,
                        max_size=settings.REDIS_POOL_MAX_SIZE,
                        timeout=settings.REDIS_POOL_TIMEOUT,
                        retry_attempts=settings.REDIS_POOL_RETRY_ATTEMPTS,
                        retry_delay=settings.REDIS_POOL_RETRY_DELAY,
                        health_check_interval=settings.REDIS_POOL_HEALTH_CHECK_INTERVAL,
                        idle_timeout=settings.REDIS_POOL_IDLE_TIMEOUT,
                    )
                    self.pools["redis"] = RedisConnectionPool(redis_config, settings.REDIS_URL)

                # Initialize TWS HTTP connection pool
                if settings.TWS_MAX_CONNECTIONS > 0 and settings.TWS_HOST:
                    tws_config = ConnectionPoolConfig(
                        pool_name="tws_http",
                        min_size=max(1, settings.TWS_MAX_CONNECTIONS // 10),
                        max_size=settings.TWS_MAX_CONNECTIONS,
                        timeout=settings.TWS_POOL_TIMEOUT,
                        retry_attempts=settings.TWS_POOL_RETRY_ATTEMPTS,
                        retry_delay=settings.TWS_POOL_RETRY_DELAY,
                    )
                    base_url = f"http://{settings.TWS_HOST}:{settings.TWS_PORT}/twsd"
                    self.pools["tws_http"] = HTTPConnectionPool(
                        tws_config,
                        base_url,
                        auth=(settings.TWS_USER, settings.TWS_PASSWORD),
                        verify=False
                    )

                # Initialize all pools
                for _pool_name, pool in self.pools.items():
                    await pool.initialize()

                self._initialized = True
                logger.info("Connection pool manager initialized with pools: %s", list(self.pools.keys()))

                # Record initialization metric
                runtime_metrics.record_gauge("connection_pool.manager.initialized", 1)

            except Exception as e:
                logger.error(f"Failed to initialize connection pool manager: {e}")
                # Cleanup any partially initialized pools
                await self._cleanup_pools()
                raise

    async def _cleanup_pools(self) -> None:
        """Cleanup all connection pools."""
        for pool in self.pools.values():
            try:
                await pool.shutdown()
            except Exception as e:
                logger.error(f"Error during pool cleanup: {e}")

    async def shutdown(self) -> None:
        """Shutdown all connection pools."""
        if self._shutdown:
            return

        self._shutdown = True

        async with self._lock:
            await self._cleanup_pools()
            self.pools.clear()
            self._initialized = False

            logger.info("Connection pool manager shutdown")

            # Record shutdown metric
            runtime_metrics.record_gauge("connection_pool.manager.initialized", 0)

    def get_pool(self, pool_name: str) -> Optional[ConnectionPool]:
        """Get a specific connection pool by name."""
        return self.pools.get(pool_name)

    def get_all_pools(self) -> Dict[str, ConnectionPool]:
        """Get all connection pools."""
        return self.pools.copy()

    def get_pool_stats(self) -> Dict[str, ConnectionPoolStats]:
        """Get statistics for all pools."""
        return {
            name: pool.get_stats()
            for name, pool in self.pools.items()
        }

    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all pools."""
        results = {}
        for name, pool in self.pools.items():
            try:
                results[name] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for pool '{name}': {e}")
                results[name] = False
        return results

    def is_healthy(self) -> bool:
        """Check if all pools are healthy."""
        if not self._initialized or self._shutdown:
            return False

        for pool in self.pools.values():
            stats = pool.get_stats()
            if stats.connection_errors > 5:  # Threshold for considering pool unhealthy
                return False

        return True

# Global connection pool manager instance
_pool_manager: Optional[ConnectionPoolManager] = None

async def get_connection_pool_manager() -> ConnectionPoolManager:
    """Get the global connection pool manager instance."""
    global _pool_manager

    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
        await _pool_manager.initialize()

    return _pool_manager

async def shutdown_connection_pool_manager() -> None:
    """Shutdown the global connection pool manager."""
    global _pool_manager

    if _pool_manager:
        await _pool_manager.shutdown()
        _pool_manager = None
