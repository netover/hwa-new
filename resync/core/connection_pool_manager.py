"""
Connection pool manager module for the Resync project.
This module provides a simplified interface to the connection pool functionality
that has been separated into individual modules following the Single Responsibility Principle.
"""

from resync.core.pools.base_pool import ConnectionPool, ConnectionPoolConfig, ConnectionPoolStats
from resync.core.pools.db_pool import DatabaseConnectionPool
from resync.core.pools.redis_pool import RedisConnectionPool
from resync.core.pools.http_pool import HTTPConnectionPool
from resync.core.pools.pool_manager import ConnectionPoolManager, get_connection_pool_manager

# Re-export the main classes and functions for backward compatibility
__all__ = [
    "ConnectionPool",
    "ConnectionPoolConfig", 
    "ConnectionPoolStats",
    "DatabaseConnectionPool",
    "RedisConnectionPool", 
    "HTTPConnectionPool",
    "ConnectionPoolManager",
    "get_connection_pool_manager"
]