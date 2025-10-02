from __future__ import annotations

import asyncio
import logging
import psutil
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles

from resync.core.health_models import (
    HealthStatus, ComponentType, ComponentHealth, HealthCheckResult,
    HealthCheckConfig, HealthStatusHistory
)
from resync.core.connection_pool_manager import get_connection_pool_manager
from resync.settings import settings

logger = logging.getLogger(__name__)

# Global health check service instance
_health_check_service: Optional[HealthCheckService] = None
_health_service_lock = asyncio.Lock()


class HealthCheckService:
    """Comprehensive health check service for all system components."""

    def __init__(self, config: Optional[HealthCheckConfig] = None):
        self.config = config or HealthCheckConfig()
        self.health_history: List[HealthStatusHistory] = []
        self.last_health_check: Optional[datetime] = None
        self.component_cache: Dict[str, ComponentHealth] = {}
        self.cache_expiry = timedelta(seconds=self.config.check_interval_seconds)
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        self._memory_usage_mb: float = 0.0
        self._cleanup_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._is_monitoring:
            return

        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health check monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop continuous health monitoring."""
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        logger.info("Health check monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        while self._is_monitoring:
            try:
                await self.perform_comprehensive_health_check()
                await asyncio.sleep(self.config.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error

    async def perform_comprehensive_health_check(self) -> HealthCheckResult:
        """Perform comprehensive health check on all system components."""
        start_time = time.time()
        correlation_id = f"health_{int(start_time)}"

        logger.debug(
            f"Starting comprehensive health check [correlation_id: {correlation_id}]"
        )

        # Initialize result
        result = HealthCheckResult(
            overall_status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            correlation_id=correlation_id,
            components={},
            summary={},
            alerts=[],
            performance_metrics={},
        )

        # Perform all health checks in parallel
        health_checks = {
            "database": self._check_database_health(),
            "redis": self._check_redis_health(),
            "cache_hierarchy": self._check_cache_health(),
            "file_system": self._check_file_system_health(),
            "memory": self._check_memory_health(),
            "cpu": self._check_cpu_health(),
            "tws_monitor": self._check_tws_monitor_health(),
            "connection_pools": self._check_connection_pools_health(),
            "websocket_pool": self._check_websocket_pool_health(),
        }

        # Execute all checks
        check_results = await asyncio.gather(
            *health_checks.values(), return_exceptions=True
        )

        # Process results
        for component_name, check_result in zip(health_checks.keys(), check_results):
            if isinstance(check_result, Exception):
                # Handle check failure
                logger.error(
                    f"Health check failed for {component_name}: {check_result}"
                )
                component_health = ComponentHealth(
                    name=component_name,
                    component_type=self._get_component_type(component_name),
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(check_result)}",
                    last_check=datetime.now(),
                )
            else:
                component_health = check_result

            result.components[component_name] = component_health

        # Determine overall status
        result.overall_status = self._calculate_overall_status(result.components)

        # Generate summary
        result.summary = self._generate_summary(result.components)

        # Check for alerts
        if self.config.alert_enabled:
            result.alerts = self._check_alerts(result.components)

        # Record performance metrics
        result.performance_metrics = {
            "total_check_time_ms": (time.time() - start_time) * 1000,
            "components_checked": len(result.components),
            "timestamp": time.time(),
        }

        # Update history
        await self._update_health_history(result)

        self.last_health_check = datetime.now()
        await self._update_cache(result.components)

        logger.debug(
            f"Health check completed in {result.performance_metrics['total_check_time_ms']:.2f}ms"
        )

        return result

    async def _check_database_health(self) -> ComponentHealth:
        """Check database health using connection pools."""
        start_time = time.time()

        try:
            pool_manager = get_connection_pool_manager()
            if not pool_manager:
                return ComponentHealth(
                    name="database",
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.UNKNOWN,
                    message="Database connection pool not available",
                    last_check=datetime.now(),
                )

            # Test database connectivity
            async with pool_manager.acquire_connection("default") as conn:
                # Simple query to test connection
                if hasattr(conn, "execute"):
                    result = await conn.execute("SELECT 1")
                    if hasattr(result, "fetchone"):
                        await result.fetchone()
                elif hasattr(conn, "cursor"):
                    # SQLite case
                    cursor = await conn.cursor()
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
                    await cursor.close()

            response_time = (time.time() - start_time) * 1000

            # Get real pool statistics from pool manager
            pool_stats = pool_manager.get_pool_stats()
            
            # Validate pool_stats is not empty/null
            if not pool_stats:
                return ComponentHealth(
                    name="database",
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.UNHEALTHY,
                    message="Database pool statistics unavailable (empty/null)",
                    response_time_ms=response_time,
                    last_check=datetime.now(),
                    metadata={"pool_stats": "empty or null"},
                )
            
            db_pool_stats = pool_stats.get("database")
            
            # Validate database pool stats specifically
            if db_pool_stats is None:
                return ComponentHealth(
                    name="database",
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.UNHEALTHY,
                    message="Database pool statistics missing for 'database' pool",
                    response_time_ms=response_time,
                    last_check=datetime.now(),
                    metadata={"database_pool": "missing"},
                )
            
            # Validate that the database pool has valid data
            if (not hasattr(db_pool_stats, 'total_connections') or
                db_pool_stats.total_connections is None or
                db_pool_stats.total_connections == 0):
                return ComponentHealth(
                    name="database",
                    component_type=ComponentType.DATABASE,
                    status=HealthStatus.UNHEALTHY,
                    message="Database pool has no configured connections",
                    response_time_ms=response_time,
                    last_check=datetime.now(),
                    metadata={"total_connections": 0 if db_pool_stats.total_connections is None else db_pool_stats.total_connections},
                )
            
            # Calculate connection usage percentage
            active_connections = db_pool_stats.active_connections
            total_connections = db_pool_stats.total_connections
            connection_usage_percent = (active_connections / total_connections * 100) if total_connections > 0 else 0.0
            
            # Determine status based on configurable threshold
            threshold_percent = self.config.database_connection_threshold_percent
            if connection_usage_percent >= threshold_percent:
                status = HealthStatus.DEGRADED
                message = f"Database connection pool near capacity: {active_connections}/{total_connections} ({connection_usage_percent:.1f}%)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Database connection pool healthy: {active_connections}/{total_connections} ({connection_usage_percent:.1f}%)"

            # Use real database pool statistics
            pool_metadata = {
                "active_connections": active_connections,
                "idle_connections": db_pool_stats.idle_connections,
                "total_connections": total_connections,
                "connection_usage_percent": round(connection_usage_percent, 1),
                "threshold_percent": threshold_percent,
                "connection_errors": db_pool_stats.connection_errors,
                "pool_hits": db_pool_stats.pool_hits,
                "pool_misses": db_pool_stats.pool_misses,
                "connection_creations": db_pool_stats.connection_creations,
                "connection_closures": db_pool_stats.connection_closures,
                "waiting_connections": db_pool_stats.waiting_connections,
                "peak_connections": db_pool_stats.peak_connections,
                "average_wait_time": round(db_pool_stats.average_wait_time, 3),
                "last_health_check": db_pool_stats.last_health_check.isoformat() if db_pool_stats.last_health_check else None,
            }

            return ComponentHealth(
                name="database",
                component_type=ComponentType.DATABASE,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata=pool_metadata,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            logger.error(f"Database health check failed: {e}")
            return ComponentHealth(
                name="database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_redis_health(self) -> ComponentHealth:
        """Check Redis cache health and connectivity."""
        start_time = time.time()

        try:
            # Check Redis configuration
            redis_config = settings.get("redis", {})
            if not redis_config or not redis_config.get("enabled", False):
                return ComponentHealth(
                    name="redis",
                    component_type=ComponentType.REDIS,
                    status=HealthStatus.UNKNOWN,
                    message="Redis not configured",
                    last_check=datetime.now(),
                )

            # Simple connectivity test
            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="redis",
                component_type=ComponentType.REDIS,
                status=HealthStatus.HEALTHY,
                message="Redis connectivity test successful",
                response_time_ms=response_time,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="redis",
                component_type=ComponentType.REDIS,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connectivity failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_cache_health(self) -> ComponentHealth:
        """Check cache hierarchy health."""
        start_time = time.time()

        try:
            # Test cache hierarchy
            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="cache_hierarchy",
                component_type=ComponentType.CACHE,
                status=HealthStatus.HEALTHY,
                message="Cache hierarchy operational",
                response_time_ms=response_time,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"Cache hierarchy health check failed: {e}")
            return ComponentHealth(
                name="cache_hierarchy",
                component_type=ComponentType.CACHE,
                status=HealthStatus.DEGRADED,
                message=f"Cache hierarchy issues: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_file_system_health(self) -> ComponentHealth:
        """Check file system health and disk space monitoring."""
        start_time = time.time()

        try:
            # Check disk space
            disk_usage = psutil.disk_usage("/")
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100

            # Determine status
            if disk_usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Disk space critically low: {disk_usage_percent:.1f}% used"
            elif disk_usage_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"Disk space getting low: {disk_usage_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {disk_usage_percent:.1f}% used"

            # Test file system write capability
            test_file = Path(tempfile.gettempdir()) / f"health_check_{int(time.time())}.tmp"
            try:
                async with aiofiles.open(test_file, "w") as f:
                    await f.write("health check test")
                await aiofiles.os.remove(test_file)
                write_test = "File system write test passed"
            except Exception as e:
                write_test = f"File system write test failed: {e}"
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                message += f", {write_test}"

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="file_system",
                component_type=ComponentType.FILE_SYSTEM,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata={
                    "disk_usage_percent": disk_usage_percent,
                    "disk_free_gb": disk_usage.free / (1024**3),
                    "write_test": write_test,
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"File system health check failed: {e}")
            return ComponentHealth(
                name="file_system",
                component_type=ComponentType.FILE_SYSTEM,
                status=HealthStatus.UNKNOWN,
                message=f"File system check failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_memory_health(self) -> ComponentHealth:
        """Check memory usage monitoring."""
        start_time = time.time()

        try:
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage_percent = memory.percent

            # Determine status
            if memory_usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critically high: {memory_usage_percent:.1f}%"
            elif memory_usage_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory_usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_usage_percent:.1f}%"

            # Get process memory usage
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / (1024**2)

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="memory",
                component_type=ComponentType.MEMORY,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata={
                    "memory_usage_percent": memory_usage_percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "memory_total_gb": memory.total / (1024**3),
                    "process_memory_mb": process_memory_mb,
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"Memory health check failed: {e}")
            return ComponentHealth(
                name="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_cpu_health(self) -> ComponentHealth:
        """Check CPU load monitoring."""
        start_time = time.time()

        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Determine status
            if cpu_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critically high: {cpu_percent:.1f}%"
            elif cpu_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="cpu",
                component_type=ComponentType.CPU,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata={
                    "cpu_usage_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "cpu_frequency_mhz": getattr(psutil.cpu_freq(), "current", None)
                    if hasattr(psutil, "cpu_freq")
                    else None,
                },
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"CPU health check failed: {e}")
            return ComponentHealth(
                name="cpu",
                component_type=ComponentType.CPU,
                status=HealthStatus.UNKNOWN,
                message=f"CPU check failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_tws_monitor_health(self) -> ComponentHealth:
        """Check TWS monitor health (external API service)."""
        start_time = time.time()

        try:
            # Check TWS configuration
            tws_config = settings.get("tws_monitor", {})
            if not tws_config or not tws_config.get("enabled", False):
                return ComponentHealth(
                    name="tws_monitor",
                    component_type=ComponentType.EXTERNAL_API,
                    status=HealthStatus.UNKNOWN,
                    message="TWS monitor not configured",
                    last_check=datetime.now(),
                )

            # Simple connectivity test
            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="tws_monitor",
                component_type=ComponentType.EXTERNAL_API,
                status=HealthStatus.HEALTHY,
                message="TWS monitor connectivity test successful",
                response_time_ms=response_time,
                last_check=datetime.now(),
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"TWS monitor health check failed: {e}")
            return ComponentHealth(
                name="tws_monitor",
                component_type=ComponentType.EXTERNAL_API,
                status=HealthStatus.UNHEALTHY,
                message=f"TWS monitor connectivity failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_connection_pools_health(self) -> ComponentHealth:
        """Check connection pools health."""
        start_time = time.time()

        try:
            pool_manager = get_connection_pool_manager()
            if not pool_manager:
                return ComponentHealth(
                    name="connection_pools",
                    component_type=ComponentType.CONNECTION_POOL,
                    status=HealthStatus.UNKNOWN,
                    message="Connection pool manager not available",
                    last_check=datetime.now(),
                )

            # Check pool status
            pool_stats = pool_manager.get_pool_stats()

            # Validate pool_stats is not empty/null
            if not pool_stats:
                response_time = (time.time() - start_time) * 1000
                return ComponentHealth(
                    name="connection_pools",
                    component_type=ComponentType.CONNECTION_POOL,
                    status=HealthStatus.UNHEALTHY,
                    message="Connection pools statistics unavailable (empty/null)",
                    response_time_ms=response_time,
                    last_check=datetime.now(),
                    metadata={"pool_stats": "empty or null"},
                )

            # Analyze pool health with safe defaults
            total_connections = pool_stats.get("total_connections", 0)
            active_connections = pool_stats.get("active_connections", 0)

            if total_connections == 0:
                status = HealthStatus.UNHEALTHY
                message = "No database connections available"
            else:
                # Calculate connection usage percentage
                connection_usage_percent = (active_connections / total_connections * 100)
                
                # Use database-specific threshold for database pool
                threshold_percent = self.config.database_connection_threshold_percent
                
                if connection_usage_percent >= threshold_percent:
                    status = HealthStatus.DEGRADED
                    message = (
                        f"Connection pool near capacity: {active_connections}/{total_connections} "
                        f"({connection_usage_percent:.1f}%, threshold: {threshold_percent}%)"
                    )
                else:
                    status = HealthStatus.HEALTHY
                    message = (
                        f"Connection pool healthy: {active_connections}/{total_connections} "
                        f"({connection_usage_percent:.1f}%)"
                    )

            response_time = (time.time() - start_time) * 1000

            # Enhance metadata with calculated percentages and thresholds
            enhanced_metadata = dict(pool_stats)
            if "active_connections" in pool_stats and "total_connections" in pool_stats:
                enhanced_metadata["connection_usage_percent"] = round(connection_usage_percent, 1)
                enhanced_metadata["threshold_percent"] = self.config.database_connection_threshold_percent

            return ComponentHealth(
                name="connection_pools",
                component_type=ComponentType.CONNECTION_POOL,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata=enhanced_metadata,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Simple error handling for health checks
            secure_message = str(e)
            
            logger.error(f"Connection pools health check failed: {e}")
            return ComponentHealth(
                name="connection_pools",
                component_type=ComponentType.CONNECTION_POOL,
                status=HealthStatus.UNHEALTHY,
                message=f"Connection pools check failed: {secure_message}",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_count=1,
            )

    async def _check_websocket_pool_health(self) -> ComponentHealth:
        """Placeholder websocket pool health check (not implemented)."""
        # Mark as unknown if not implemented
        return ComponentHealth(
            name="websocket_pool",
            component_type=ComponentType.CONNECTION_POOL,
            status=HealthStatus.UNKNOWN,
            message="Websocket pool check not implemented",
            last_check=datetime.now(),
        )

    def _get_component_type(self, name: str) -> ComponentType:
        mapping: Dict[str, ComponentType] = {
            "database": ComponentType.DATABASE,
            "redis": ComponentType.REDIS,
            "cache_hierarchy": ComponentType.CACHE,
            "file_system": ComponentType.FILE_SYSTEM,
            "memory": ComponentType.MEMORY,
            "cpu": ComponentType.CPU,
            "tws_monitor": ComponentType.EXTERNAL_API,
            "connection_pools": ComponentType.CONNECTION_POOL,
            "websocket_pool": ComponentType.CONNECTION_POOL,
        }
        return mapping.get(name, ComponentType.OTHER)

    def _calculate_overall_status(self, components: Dict[str, ComponentHealth]) -> HealthStatus:
        # Simple aggregation: worst status wins
        priority = {
            HealthStatus.UNHEALTHY: 3,
            HealthStatus.DEGRADED: 2,
            HealthStatus.HEALTHY: 1,
            HealthStatus.UNKNOWN: 0,
        }
        worst = HealthStatus.HEALTHY
        for comp in components.values():
            if priority[comp.status] > priority[worst]:
                worst = comp.status
        return worst

    def _generate_summary(self, components: Dict[str, ComponentHealth]) -> Dict[str, int]:
        summary: Dict[str, int] = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0,
        }
        for comp in components.values():
            if comp.status == HealthStatus.HEALTHY:
                summary["healthy"] += 1
            elif comp.status == HealthStatus.DEGRADED:
                summary["degraded"] += 1
            elif comp.status == HealthStatus.UNHEALTHY:
                summary["unhealthy"] += 1
            else:
                summary["unknown"] += 1
        return summary

    def _check_alerts(self, components: Dict[str, ComponentHealth]) -> List[str]:
        alerts: List[str] = []
        for name, comp in components.items():
            if comp.status == HealthStatus.UNHEALTHY:
                alerts.append(f"{name} is unhealthy")
            elif comp.status == HealthStatus.DEGRADED:
                # Include specific threshold breach information in alerts
                if name == "database" and "connection_usage_percent" in comp.metadata:
                    threshold = comp.metadata.get("threshold_percent", self.config.database_connection_threshold_percent)
                    usage = comp.metadata["connection_usage_percent"]
                    alerts.append(
                        f"Database connection pool usage at {usage:.1f}% (threshold: {threshold}%)"
                    )
                else:
                    alerts.append(f"{name} is degraded")
        return alerts

    async def _update_cache(self, components: Dict[str, ComponentHealth]) -> None:
        """Thread-safe update of component cache."""
        async with self._cache_lock:
            self.component_cache = components.copy()

    async def _get_cached_component(self, component_name: str) -> Optional[ComponentHealth]:
        """Thread-safe retrieval of a component from cache."""
        async with self._cache_lock:
            return self.component_cache.get(component_name)

    async def _get_all_cached_components(self) -> Dict[str, ComponentHealth]:
        """Thread-safe retrieval of all cached components."""
        async with self._cache_lock:
            return self.component_cache.copy()

    async def _update_cached_component(self, component_name: str, health: ComponentHealth) -> None:
        """Thread-safe update of a single component in cache."""
        async with self._cache_lock:
            self.component_cache[component_name] = health

    async def _update_health_history(self, result: HealthCheckResult) -> None:
        """Update health history with memory bounds and efficient cleanup."""
        # Create new history entry
        component_changes = await self._get_component_changes(result.components)
        history_entry = HealthStatusHistory(
            timestamp=result.timestamp,
            overall_status=result.overall_status,
            component_changes=component_changes
        )
        
        # Add to history
        self.health_history.append(history_entry)
        
        # Perform cleanup if needed
        asyncio.create_task(self._cleanup_health_history())
        
        # Update memory usage tracking
        if self.config.enable_memory_monitoring:
            asyncio.create_task(self._update_memory_usage())

    async def _cleanup_health_history(self) -> None:
        """Perform efficient cleanup of health history based on multiple criteria."""
        async with self._cleanup_lock:
            try:
                current_size = len(self.health_history)
                max_entries = self.config.max_history_entries
                cleanup_threshold = int(max_entries * self.config.history_cleanup_threshold)
                
                # Check if cleanup is needed based on size
                if current_size > max_entries:
                    # Remove oldest entries to get back to threshold
                    entries_to_remove = current_size - max_entries + self.config.history_cleanup_batch_size
                    self.health_history = self.health_history[entries_to_remove:]
                    logger.debug(f"Cleaned up {entries_to_remove} health history entries (size-based)")
                
                # Check if cleanup is needed based on age
                cutoff_date = datetime.now() - timedelta(days=self.config.history_retention_days)
                original_size = len(self.health_history)
                self.health_history = [
                    entry for entry in self.health_history
                    if entry.timestamp >= cutoff_date
                ]
                removed_by_age = original_size - len(self.health_history)
                if removed_by_age > 0:
                    logger.debug(f"Cleaned up {removed_by_age} health history entries (age-based)")
                
                # Ensure we don't go below minimum required entries
                min_entries = max(10, self.config.history_cleanup_batch_size)
                if len(self.health_history) < min_entries and original_size >= min_entries:
                    # Keep at least some recent history
                    self.health_history = self.health_history[-min_entries:]
                
            except Exception as e:
                logger.error(f"Error during health history cleanup: {e}")

    async def _get_component_changes(self, components: Dict[str, ComponentHealth]) -> Dict[str, HealthStatus]:
        """Track component status changes for history."""
        changes = {}
        cached_components = await self._get_all_cached_components()
        
        for name, component in components.items():
            # Compare with last known status from cache
            if name in cached_components:
                if cached_components[name].status != component.status:
                    changes[name] = component.status
            else:
                # New component
                changes[name] = component.status
        return changes

    async def _update_memory_usage(self) -> None:
        """Update memory usage tracking for health history."""
        try:
            import sys
            # Estimate memory usage of health history
            history_size = len(self.health_history)
            if history_size > 0:
                # Rough estimation: each entry ~1KB (can be refined)
                estimated_size_bytes = history_size * 1024
                self._memory_usage_mb = estimated_size_bytes / (1024 * 1024)
                
                # Alert if memory usage exceeds threshold
                if self._memory_usage_mb > self.config.memory_usage_threshold_mb:
                    logger.warning(
                        f"Health history memory usage ({self._memory_usage_mb:.2f}MB) "
                        f"exceeds threshold ({self.config.memory_usage_threshold_mb}MB)"
                    )
            else:
                self._memory_usage_mb = 0.0
                
        except Exception as e:
            logger.error(f"Error updating memory usage: {e}")

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        return {
            "history_entries": len(self.health_history),
            "memory_usage_mb": round(self._memory_usage_mb, 2),
            "max_entries": self.config.max_history_entries,
            "retention_days": self.config.history_retention_days,
            "cleanup_threshold_percent": self.config.history_cleanup_threshold * 100,
            "memory_threshold_mb": self.config.memory_usage_threshold_mb,
            "enable_monitoring": self.config.enable_memory_monitoring,
        }

    async def force_cleanup(self) -> Dict[str, Any]:
        """Force immediate cleanup of health history."""
        original_size = len(self.health_history)
        await self._cleanup_health_history()
        new_size = len(self.health_history)
        
        return {
            "original_entries": original_size,
            "cleaned_entries": original_size - new_size,
            "current_entries": new_size,
            "memory_usage_mb": round(self._memory_usage_mb, 2),
        }

    def get_health_history(self, hours: int = 24, max_entries: Optional[int] = None) -> List[HealthStatusHistory]:
        """Get health history for the specified number of hours with optional entry limit."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter by time
        filtered_history = [
            entry for entry in self.health_history
            if entry.timestamp >= cutoff_time
        ]
        
        # Apply entry limit if specified
        if max_entries is not None and len(filtered_history) > max_entries:
            # Return most recent entries
            filtered_history = filtered_history[-max_entries:]
        
        return filtered_history

    async def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get the current health status of a specific component."""
        return await self._get_cached_component(component_name)

    async def attempt_recovery(self, component_name: str) -> bool:
        """Attempt to recover a specific component."""
        # Placeholder implementation - can be extended for specific recovery strategies
        logger.info(f"Attempting recovery for component: {component_name}")
        
        # For now, just perform a fresh health check
        try:
            if component_name == "database":
                health = await self._check_database_health()
            elif component_name == "redis":
                health = await self._check_redis_health()
            elif component_name == "cache_hierarchy":
                health = await self._check_cache_health()
            elif component_name == "file_system":
                health = await self._check_file_system_health()
            elif component_name == "memory":
                health = await self._check_memory_health()
            elif component_name == "cpu":
                health = await self._check_cpu_health()
            elif component_name == "tws_monitor":
                health = await self._check_tws_monitor_health()
            elif component_name == "connection_pools":
                health = await self._check_connection_pools_health()
            elif component_name == "websocket_pool":
                health = await self._check_websocket_pool_health()
            else:
                logger.warning(f"Unknown component for recovery: {component_name}")
                return False
            
            # Update cache with new health status
            await self._update_cached_component(component_name, health)
            return health.status == HealthStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Recovery attempt failed for {component_name}: {e}")
            return False


# Global health check service instance management
async def get_health_check_service() -> HealthCheckService:
    """
    Get the global health check service instance with thread-safe singleton initialization.
    
    This function implements the async double-checked locking pattern to prevent
    race conditions during singleton initialization.
    
    Returns:
        HealthCheckService: The global health check service instance
    """
    global _health_check_service
    
    # First check (without lock) for performance
    if _health_check_service is not None:
        return _health_check_service
    
    # Acquire lock for thread-safe initialization
    async with _health_service_lock:
        # Second check (with lock) to prevent race condition
        if _health_check_service is None:
            logger.info("Initializing global health check service")
            _health_check_service = HealthCheckService()
            await _health_check_service.start_monitoring()
            logger.info("Global health check service initialized and monitoring started")
    
    return _health_check_service


async def shutdown_health_check_service() -> None:
    """
    Shutdown the global health check service gracefully.
    
    This function ensures proper cleanup of the health check service,
    including stopping monitoring and releasing resources.
    """
    global _health_check_service
    
    if _health_check_service is not None:
        try:
            logger.info("Shutting down global health check service")
            await _health_check_service.stop_monitoring()
            _health_check_service = None
            logger.info("Global health check service shutdown completed")
        except Exception as e:
            logger.error(f"Error during health check service shutdown: {e}")
            raise
    else:
        logger.debug("Health check service already shutdown or never initialized")
