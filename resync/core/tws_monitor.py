"""
Advanced monitoring system for TWS operations and performance metrics.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from resync.core.circuit_breaker import tws_api_breaker, tws_job_status_breaker
from resync.core.llm_monitor import llm_cost_monitor

logger = logging.getLogger(__name__)


@dataclass
class TWSMetrics:
    """TWS-specific performance metrics."""

    # API Performance
    api_response_times: List[float] = field(default_factory=list)
    api_error_count: int = 0
    api_success_count: int = 0

    # Cache Performance
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_ratio: float = 0.0

    # Job Processing
    jobs_processed: int = 0
    jobs_failed: int = 0
    avg_job_processing_time: float = 0.0

    # LLM Usage
    llm_requests: int = 0
    llm_errors: int = 0
    llm_total_cost: float = 0.0

    # Circuit Breaker
    circuit_breaker_trips: int = 0
    circuit_breaker_state: str = "closed"

    # Memory Usage
    memory_usage_mb: float = 0.0
    peak_memory_usage_mb: float = 0.0


class TWSMonitor:
    """
    Advanced monitoring system for TWS operations.

    Features:
    - Real-time performance metrics
    - Circuit breaker monitoring
    - Cache performance tracking
    - LLM cost monitoring
    - Memory usage tracking
    - Alert system for anomalies
    """

    def __init__(self):
        """Initialize TWS monitor."""
        self.metrics = TWSMetrics()
        self.metrics_history: List[TWSMetrics] = []
        self.alerts: List[Dict[str, Any]] = []

        # Monitoring intervals
        self.metrics_collection_interval = 60  # seconds
        self.alert_check_interval = 30  # seconds

        # Alert thresholds
        self.alert_thresholds = {
            "api_error_rate": 0.1,  # 10% error rate
            "cache_hit_ratio": 0.7,  # 70% hit ratio
            "llm_cost_daily": 50.0,  # $50 daily limit
            "circuit_breaker_open": True,
            "memory_usage": 500.0,  # 500MB limit
        }

        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False

    async def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self.is_running:
            return

        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("TWS monitoring system started")

    async def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("TWS monitoring system stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Collect current metrics
                await self._collect_metrics()

                # Check for alerts
                await self._check_alerts()

                # Store metrics snapshot
                self.metrics_history.append(
                    self.metrics.__class__(**self.metrics.__dict__)
                )

                # Keep only last 24 hours of history
                cutoff_time = time.time() - (24 * 3600)
                self.metrics_history = [
                    m
                    for m in self.metrics_history
                    if time.time() - cutoff_time < 24 * 3600
                ]

                await asyncio.sleep(self.metrics_collection_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Brief pause on error

    async def _collect_metrics(self) -> None:
        """Collect current system metrics."""
        # API metrics
        self.metrics.api_response_times.append(time.time())
        # Keep only last 100 response times
        self.metrics.api_response_times = self.metrics.api_response_times[-100:]

        # Circuit breaker metrics
        api_stats = tws_api_breaker.get_stats()
        job_stats = tws_job_status_breaker.get_stats()

        if api_stats["state"] == "open" or job_stats["state"] == "open":
            self.metrics.circuit_breaker_trips += 1
            self.metrics.circuit_breaker_state = "open"
        else:
            self.metrics.circuit_breaker_state = "closed"

        # Memory usage (simplified)
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()
        self.metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
        self.metrics.peak_memory_usage_mb = max(
            self.metrics.peak_memory_usage_mb, self.metrics.memory_usage_mb
        )

        # LLM metrics
        llm_report = llm_cost_monitor.get_usage_report()
        self.metrics.llm_requests = llm_report["total_requests"]
        self.metrics.llm_total_cost = llm_report["total_cost_usd"]

    async def _check_alerts(self) -> None:
        """Check for alert conditions."""
        alerts_to_add = []

        # API error rate check
        if (
            self.metrics.api_error_count / max(1, self.metrics.api_success_count)
            > self.alert_thresholds["api_error_rate"]
        ):
            alerts_to_add.append(
                {
                    "type": "high_api_error_rate",
                    "message": f"API error rate: {self.metrics.api_error_count / max(1, self.metrics.api_success_count):.2%}",
                    "severity": "warning",
                    "timestamp": time.time(),
                }
            )

        # Cache hit ratio check
        total_cache_requests = self.metrics.cache_hits + self.metrics.cache_misses
        if total_cache_requests > 0:
            hit_ratio = self.metrics.cache_hits / total_cache_requests
            if hit_ratio < self.alert_thresholds["cache_hit_ratio"]:
                alerts_to_add.append(
                    {
                        "type": "low_cache_hit_ratio",
                        "message": f"Cache hit ratio: {hit_ratio:.2%}",
                        "severity": "info",
                        "timestamp": time.time(),
                    }
                )

        # LLM cost check
        llm_report = llm_cost_monitor.get_usage_report()
        daily_cost = sum(llm_report["daily_costs"].values())
        if daily_cost > self.alert_thresholds["llm_cost_daily"]:
            alerts_to_add.append(
                {
                    "type": "high_llm_cost",
                    "message": f"Daily LLM cost: ${daily_cost:.2f}",
                    "severity": "warning",
                    "timestamp": time.time(),
                }
            )

        # Circuit breaker check
        if self.metrics.circuit_breaker_state == "open":
            alerts_to_add.append(
                {
                    "type": "circuit_breaker_open",
                    "message": "Circuit breaker is open - service unavailable",
                    "severity": "critical",
                    "timestamp": time.time(),
                }
            )

        # Memory usage check
        if self.metrics.memory_usage_mb > self.alert_thresholds["memory_usage"]:
            alerts_to_add.append(
                {
                    "type": "high_memory_usage",
                    "message": f"Memory usage: {self.metrics.memory_usage_mb:.1f}MB",
                    "severity": "warning",
                    "timestamp": time.time(),
                }
            )

        # Add alerts
        for alert in alerts_to_add:
            self.alerts.append(alert)
            logger.log(
                logging.WARNING if alert["severity"] != "critical" else logging.ERROR,
                f"TWS Alert [{alert['severity'].upper()}]: {alert['message']}",
            )

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        return {
            "api_response_times": len(self.metrics.api_response_times),
            "api_error_count": self.metrics.api_error_count,
            "api_success_count": self.metrics.api_success_count,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "cache_hit_ratio": self.metrics.cache_hit_ratio,
            "jobs_processed": self.metrics.jobs_processed,
            "jobs_failed": self.metrics.jobs_failed,
            "llm_requests": self.metrics.llm_requests,
            "llm_total_cost": self.metrics.llm_total_cost,
            "circuit_breaker_state": self.metrics.circuit_breaker_state,
            "memory_usage_mb": self.metrics.memory_usage_mb,
            "peak_memory_usage_mb": self.metrics.peak_memory_usage_mb,
        }

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        return sorted(self.alerts[-limit:], key=lambda x: x["timestamp"], reverse=True)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            "current_metrics": self.get_current_metrics(),
            "alerts": self.get_alerts(10),
            "llm_report": llm_cost_monitor.get_usage_report(),
            "circuit_breaker_stats": {
                "tws_api": tws_api_breaker.get_stats(),
                "tws_jobs": tws_job_status_breaker.get_stats(),
            },
        }


# Global instance
tws_monitor = TWSMonitor()
