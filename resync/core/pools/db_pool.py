"""
Database connection pool implementation for the Resync project.
Separated to follow Single Responsibility Principle.
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from resync.core.exceptions import DatabaseError
from resync.core.metrics import runtime_metrics
from resync.settings import settings
from resync.core.pools.base_pool import ConnectionPool, ConnectionPoolConfig

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class DatabaseConnectionPool(ConnectionPool[AsyncEngine]):
    """Database connection pool with advanced features."""

    def __init__(self, config: ConnectionPoolConfig, database_url: str):
        super().__init__(config)
        self.database_url = database_url
        self._async_engine: Optional[AsyncEngine] = None
        self._async_sessionmaker: Optional[async_sessionmaker] = None

    async def _setup_pool(self) -> None:
        """Setup database connection pool with optimized settings."""
        try:
            # Configure async SQLAlchemy engine with connection pooling
            # Use the database URL from settings with appropriate pooling
            self._async_engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,  # Use queue-based pooling for async
                pool_size=self.config.min_size,
                max_overflow=self.config.max_size - self.config.min_size,
                pool_pre_ping=True,  # Verify connections are alive before use
                pool_recycle=self.config.max_lifetime,  # Recycle connections after max lifetime
                echo=False,  # Turn off SQL echo in production
                pool_timeout=self.config.connection_timeout
            )

            # Create async sessionmaker for creating sessions
            self._async_sessionmaker = async_sessionmaker(
                self._async_engine,
                expire_on_commit=False,
                class_=None,
                sync_session_class=None
            )

            logger.info(f"Database connection pool '{self.config.pool_name}' initialized with {self.config.min_size}-{self.config.max_size} connections")
        except Exception as e:
            logger.error(f"Failed to setup database connection pool: {e}")
            raise DatabaseError(f"Failed to setup database connection pool: {e}") from e

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

    async def _close_pool(self) -> None:
        """Close the database connection pool."""
        if self._async_engine:
            await self._async_engine.dispose()
            logger.info(f"Database connection pool '{self.config.pool_name}' closed")