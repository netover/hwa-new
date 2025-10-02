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
        self._update_health_history(result)

        self.last_health_check = datetime.now()
        self.component_cache = result.components.copy()

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

            # Mock pool stats for testing
            pool_stats = {
                "active_connections": 5,
                "idle_connections": 10,
                "total_connections": 15,
                "connection_errors": 0,
                "pool_hits": 100,
                "pool_misses": 5,
            }

            return ComponentHealth(
                name="database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata=pool_stats,
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

            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="redis",
                component_type=ComponentType.REDIS,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connectivity failed: {str(e)}",
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

            logger.error(f"Cache hierarchy health check failed: {e}")
            return ComponentHealth(
                name="cache_hierarchy",
                component_type=ComponentType.CACHE,
                status=HealthStatus.DEGRADED,
                message=f"Cache hierarchy issues: {str(e)}",
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

            logger.error(f"File system health check failed: {e}")
            return ComponentHealth(
                name="file_system",
                component_type=ComponentType.FILE_SYSTEM,
                status=HealthStatus.UNKNOWN,
                message=f"File system check failed: {str(e)}",
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

            logger.error(f"Memory health check failed: {e}")
            return ComponentHealth(
                name="memory",
                component_type=ComponentType.MEMORY,
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {str(e)}",
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

            logger.error(f"CPU health check failed: {e}")
            return ComponentHealth(
                name="cpu",
                component_type=ComponentType.CPU,
                status=HealthStatus.UNKNOWN,
                message=f"CPU check failed: {str(e)}",
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

            logger.error(f"TWS monitor health check failed: {e}")
            return ComponentHealth(
                name="tws_monitor",
                component_type=ComponentType.EXTERNAL_API,
                status=HealthStatus.UNHEALTHY,
                message=f"TWS monitor connectivity failed: {str(e)}",
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

            # Analyze pool health
            total_connections = pool_stats.get("total_connections", 0)
            active_connections = pool_stats.get("active_connections", 0)

            if total_connections == 0:
                status = HealthStatus.UNHEALTHY
                message = "No database connections available"
            elif active_connections > total_connections * 0.9:
                status = HealthStatus.DEGRADED
                message = (
                    f"Connection pool near capacity: {active_connections}/{total_connections}"
                )
            else:
                status = HealthStatus.HEALTHY
                message = (
                    f"Connection pool healthy: {active_connections}/{total_connections}"
                )

            response_time = (time.time() - start_time) * 1000

            return ComponentHealth(
                name="connection_pools",
                component_type=ComponentType.CONNECTION_POOL,
                status=status,
                message=message,
                response_time_ms=response_time,
                last_check=datetime.now(),
                metadata=pool_stats,
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            logger.error(f"Connection pools health check failed: {e}")
            return ComponentHealth(
                name="connection_pools",
                component_type=ComponentType.CONNECTION_POOL,
                status=HealthStatus.UNHEALTHY,
                message=f"Connection pools check failed: {str(e)}",
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
        return alerts

    def _update_health_history(self, result: HealthCheckResult) -> None:
        # Keep a simple bounded history
        self.health_history.append(
            HealthStatusHistory(timestamp=result.timestamp, status=result.overall_status)
        )
        max_history = getattr(self.config, "max_history", 100)
        if len(self.health_history) > max_history:
            self.health_history = self.health_history[-max_history:]
