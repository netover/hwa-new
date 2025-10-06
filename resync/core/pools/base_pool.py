"""
Connection pool base classes and configuration for the Resync project.
Separated to follow Single Responsibility Principle.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from resync.core.metrics import runtime_metrics

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
    idle_timeout: int = 300  # 5 minutes
    connection_timeout: int = 30  # 30 seconds
    health_check_interval: int = 60  # 1 minute
    max_lifetime: int = 1800  # 30 minutes


class ConnectionPool(ABC, Generic[T]):
    """Abstract base class for connection pools."""

    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self._initialized = False
        self._shutdown = False
        self.stats = ConnectionPoolStats(pool_name=config.pool_name)
        self._lock = asyncio.Lock()  # For thread-safe operations
        self._wait_times = []  # Track connection acquisition times for metrics

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
                logger.info(f"Initialized {self.config.pool_name} connection pool")
            except Exception as e:
                logger.error(f"Failed to initialize {self.config.pool_name} connection pool: {e}")
                raise

    async def _setup_pool(self) -> None:
        """Setup the connection pool - to be implemented by subclasses."""
        pass

    @asynccontextmanager
    @abstractmethod
    async def get_connection(self):
        """Get a connection from the pool."""
        pass

    async def close(self) -> None:
        """Close the connection pool."""
        if not self._initialized or self._shutdown:
            return

        async with self._lock:
            if self._shutdown:
                return

            try:
                await self._close_pool()
                self._shutdown = True
                logger.info(f"Closed {self.config.pool_name} connection pool")
            except Exception as e:
                logger.error(f"Error closing {self.config.pool_name} connection pool: {e}")
                raise

    async def _close_pool(self) -> None:
        """Close the connection pool - to be implemented by subclasses."""
        pass

    def update_wait_time(self, wait_time: float) -> None:
        """Update wait time statistics."""
        self._wait_times.append(wait_time)
        # Keep only last 1000 measurements to prevent memory issues
        if len(self._wait_times) > 1000:
            self._wait_times = self._wait_times[-1000:]
        
        # Calculate average
        if self._wait_times:
            self.stats.average_wait_time = sum(self._wait_times) / len(self._wait_times)

    async def health_check(self) -> bool:
        """Perform a health check on the pool."""
        if not self._initialized or self._shutdown:
            return False

        try:
            # Try to get and use a connection briefly
            async with self.get_connection() as conn:
                # The actual health check depends on the connection type
                # This is a basic check that just tries to acquire a connection
                pass
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {self.config.pool_name}: {e}")
            return False