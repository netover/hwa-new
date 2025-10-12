"""
Advanced Circuit Breaker pattern implementation with latency-based adaptive thresholds.

This module provides both traditional failure-based circuit breakers and advanced
latency-aware adaptive circuit breakers for production reliability.

Features:
- Traditional circuit breaker (backward compatible)
- Latency-based adaptive circuit breaker
- P95/P99 latency monitoring
- Auto-tuning thresholds based on performance
- Sliding window metrics
- Production-ready with comprehensive observability
"""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Deque, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    expected_exception: type[Exception] = Exception
    success_threshold: int = 3  # Successes needed in half-open to close


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""

    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    total_successes: int = 0


@dataclass
class LatencyMetrics:
    """Latency performance metrics for adaptive circuit breaker."""

    # Sliding window for latencies (last N requests)
    latencies: Deque[float] = field(default_factory=lambda: deque(maxlen=100))

    # Thresholds adaptativos
    p50_threshold: float = 0.1  # 100ms
    p95_threshold: float = 0.3  # 300ms
    p99_threshold: float = 0.5  # 500ms

    # Counters
    slow_requests: int = 0
    total_measurements: int = 0

    # Degradation state
    is_degraded: bool = False
    degradation_start: float = 0.0

    def add_latency(self, latency: float) -> None:
        """Add a latency measurement."""
        self.latencies.append(latency)
        self.total_measurements += 1

        # Check if request is slow
        if latency > self.p95_threshold:
            self.slow_requests += 1

    def calculate_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles."""
        if not self.latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        return {
            "p50": sorted_latencies[int(0.50 * n)] if n > 0 else 0.0,
            "p95": sorted_latencies[int(0.95 * n)] if n > 1 else 0.0,
            "p99": sorted_latencies[int(0.99 * n)] if n > 2 else 0.0,
            "avg": statistics.mean(self.latencies)
        }

    def is_latency_degraded(self) -> bool:
        """Determine if latency is degraded."""
        if len(self.latencies) < 10:  # Minimum samples
            return False

        percentiles = self.calculate_percentiles()

        # Degradation criteria (configurable)
        conditions = [
            percentiles["p95"] > self.p95_threshold,
            percentiles["p99"] > self.p99_threshold,
            self.slow_requests / max(1, self.total_measurements) > 0.1  # 10% slow requests
        ]

        return any(conditions)


@dataclass
class AdaptiveCircuitBreakerConfig:
    """Configuration for adaptive circuit breaker."""

    # Original configurations
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    expected_exception: type[Exception] = Exception
    success_threshold: int = 3

    # NEW: Latency configurations
    latency_threshold_p95: float = 0.3  # 300ms
    latency_threshold_p99: float = 0.5  # 500ms
    latency_window_size: int = 100      # Last 100 requests

    # NEW: Adaptive configurations
    enable_adaptive_thresholds: bool = True
    adaptive_factor: float = 1.5        # Multiplier for dynamic adjustment
    min_samples_for_adaptation: int = 50

    # NEW: Degradation configurations
    degradation_factor: float = 2.0     # Multiplier when degraded
    fast_recovery_enabled: bool = True  # Fast recovery if latency improves


class CircuitBreaker:
    """
    Circuit breaker implementation for handling TWS API failures.

    Protects against cascading failures by temporarily stopping
    requests to a failing service.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """Initialize circuit breaker."""
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "CircuitBreaker":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if exc_type and issubclass(exc_type, self.config.expected_exception):
            await self.record_failure()
            raise
        else:
            await self.record_success()

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Original exception if function fails
        """
        if not await self.can_execute():
            raise CircuitBreakerOpen(f"Circuit breaker is {self.state.value}")

        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            if isinstance(e, self.config.expected_exception):
                await self.record_failure()
            raise

    async def can_execute(self) -> bool:
        """Check if requests can be executed."""
        async with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    await self._set_state(CircuitBreakerState.HALF_OPEN)
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return True
            return False

    async def record_success(self) -> None:
        """Record a successful execution."""
        async with self._lock:
            now = time.time()
            self.stats.successes += 1
            self.stats.total_successes += 1
            self.stats.last_success_time = now

            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.stats.successes >= self.config.success_threshold:
                    await self._set_state(CircuitBreakerState.CLOSED)
                    logger.info("Circuit breaker closed after successful recovery")

    async def record_failure(self) -> None:
        """Record a failed execution."""
        async with self._lock:
            now = time.time()
            self.stats.failures += 1
            self.stats.total_failures += 1
            self.stats.last_failure_time = now

            if (
                self.state == CircuitBreakerState.CLOSED
                and self.stats.failures >= self.config.failure_threshold
            ):
                await self._set_state(CircuitBreakerState.OPEN)
                logger.warning(
                    f"Circuit breaker opened after {self.stats.failures} failures"
                )
            elif self.state == CircuitBreakerState.HALF_OPEN:
                await self._set_state(CircuitBreakerState.OPEN)
                logger.warning(
                    "Circuit breaker reopened after failure in half-open state"
                )

    async def _set_state(self, new_state: CircuitBreakerState) -> None:
        """Set circuit breaker state."""
        old_state = self.state
        self.state = new_state

        if new_state == CircuitBreakerState.HALF_OPEN:
            self.stats.successes = 0
        elif new_state == CircuitBreakerState.CLOSED:
            self.stats.failures = 0

        logger.debug(
            "circuit_breaker_state_changed",
            old_state=old_state.value,
            new_state=new_state.value,
        )

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.state != CircuitBreakerState.OPEN:
            return False

        time_since_failure = time.time() - self.stats.last_failure_time
        return time_since_failure >= self.config.recovery_timeout

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.state.value,
            "failures": self.stats.failures,
            "successes": self.stats.successes,
            "total_requests": self.stats.total_requests,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time,
            "failure_rate": (
                self.stats.total_failures / max(1, self.stats.total_requests)
            ),
        }


class AdaptiveCircuitBreaker(CircuitBreaker):
    """
    Adaptive Circuit Breaker based on latency AND failures.

    Expands the original implementation with:
    - P95/P99 latency monitoring
    - Adaptive thresholds
    - Performance-based recovery
    - Gradual degradation
    """

    def __init__(self, config: Optional[AdaptiveCircuitBreakerConfig] = None):
        """Initialize adaptive circuit breaker."""
        # Initialize parent class
        base_config = CircuitBreakerConfig(
            failure_threshold=config.failure_threshold if config else 5,
            recovery_timeout=config.recovery_timeout if config else 30.0,
            expected_exception=config.expected_exception if config else Exception,
            success_threshold=config.success_threshold if config else 3
        )
        super().__init__(base_config)

        # Extended configuration
        self.adaptive_config = config or AdaptiveCircuitBreakerConfig()

        # New latency metrics
        self.latency_metrics = LatencyMetrics()

        # Adaptive state
        self._last_adaptation = time.time()
        self._adaptation_interval = 60.0  # Re-evaluate every minute

    async def call_with_latency(
        self,
        func: Callable[..., T],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """
        Execute function with latency monitoring AND circuit breaking.

        NEW method that combines original functionality with latency.
        """
        if not await self.can_execute():
            raise CircuitBreakerOpen(f"Circuit breaker is {self.state.value}")

        # Measure latency
        start_time = time.time()

        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Calculate latency
            latency = time.time() - start_time

            # Record success with latency
            await self._record_success_with_latency(latency)

            return result

        except Exception as e:
            # Calculate latency even on error
            latency = time.time() - start_time
            self.latency_metrics.add_latency(latency)

            if isinstance(e, self.config.expected_exception):
                await self.record_failure()
            raise

    async def _record_success_with_latency(self, latency: float) -> None:
        """Record success considering latency."""
        async with self._lock:
            # Add latency to metrics
            self.latency_metrics.add_latency(latency)

            # Check if should adapt thresholds
            await self._adapt_thresholds_if_needed()

            # Determine if request was "slow" (success but degraded)
            is_slow = await self._is_request_slow(latency)

            if not is_slow:
                # Normal success - use original logic
                await self.record_success()
            else:
                # Slow success - considered as degradation
                await self._handle_slow_success(latency)

    async def _is_request_slow(self, latency: float) -> bool:
        """Determine if request is considered slow."""
        # Use adaptive thresholds if enabled
        if self.adaptive_config.enable_adaptive_thresholds:
            percentiles = self.latency_metrics.calculate_percentiles()
            dynamic_threshold = percentiles.get("p95", 0) * self.adaptive_config.adaptive_factor
            return latency > max(dynamic_threshold, self.adaptive_config.latency_threshold_p95)

        return latency > self.adaptive_config.latency_threshold_p95

    async def _handle_slow_success(self, latency: float) -> None:
        """Handle slow successes as degradation indicator."""
        self.stats.successes += 1
        self.stats.total_successes += 1
        self.stats.last_success_time = time.time()

        # Check if system is degraded by latency
        if self.latency_metrics.is_latency_degraded():

            if self.state == CircuitBreakerState.CLOSED:
                # Consider opening circuit due to latency degradation
                degradation_ratio = (
                    self.latency_metrics.slow_requests /
                    max(1, self.latency_metrics.total_measurements)
                )

                # More permissive threshold than complete failures
                if degradation_ratio > 0.2:  # 20% slow requests
                    await self._set_state(CircuitBreakerState.HALF_OPEN)
                    logger.warning(
                        "circuit_breaker_degraded",
                        latency=latency,
                        degradation_ratio=degradation_ratio,
                        p95=self.latency_metrics.calculate_percentiles()["p95"]
                    )

    async def _adapt_thresholds_if_needed(self) -> None:
        """Adapt thresholds based on performance history."""
        if not self.adaptive_config.enable_adaptive_thresholds:
            return

        now = time.time()
        if (now - self._last_adaptation) < self._adaptation_interval:
            return

        if len(self.latency_metrics.latencies) < self.adaptive_config.min_samples_for_adaptation:
            return

        # Calculate new thresholds based on history
        percentiles = self.latency_metrics.calculate_percentiles()

        # Adapt thresholds (with safety minimums)
        new_p95_threshold = max(
            percentiles["p95"] * self.adaptive_config.adaptive_factor,
            0.1  # Minimum 100ms
        )

        new_p99_threshold = max(
            percentiles["p99"] * self.adaptive_config.adaptive_factor,
            0.2  # Minimum 200ms
        )

        # Update only if difference is significant (avoid oscillation)
        if abs(new_p95_threshold - self.adaptive_config.latency_threshold_p95) > 0.05:
            self.adaptive_config.latency_threshold_p95 = new_p95_threshold
            logger.info(
                "circuit_breaker_threshold_adapted",
                new_p95=new_p95_threshold,
                new_p99=new_p99_threshold,
                sample_size=len(self.latency_metrics.latencies)
            )

        self._last_adaptation = now

    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Enhanced statistics with latency metrics."""
        base_stats = self.get_stats()

        percentiles = self.latency_metrics.calculate_percentiles()

        return {
            **base_stats,
            # Latency metrics
            "latency_percentiles": percentiles,
            "slow_requests": self.latency_metrics.slow_requests,
            "degradation_ratio": (
                self.latency_metrics.slow_requests /
                max(1, self.latency_metrics.total_measurements)
            ),
            # Adaptive configurations
            "adaptive_p95_threshold": self.adaptive_config.latency_threshold_p95,
            "adaptive_p99_threshold": self.adaptive_config.latency_threshold_p99,
            "is_latency_degraded": self.latency_metrics.is_latency_degraded(),
            # System state
            "sample_count": len(self.latency_metrics.latencies),
            "last_adaptation": self._last_adaptation
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""


# Global circuit breakers for TWS services (traditional)
tws_api_breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30.0,
        expected_exception=Exception,  # Broad exception handling for TWS
    )
)

tws_job_status_breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=3, recovery_timeout=15.0, expected_exception=Exception
    )
)

llm_api_breaker = CircuitBreaker(
    CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0,  # Longer recovery for LLM APIs
        expected_exception=Exception,
    )
)

# Global adaptive circuit breakers for enhanced reliability
adaptive_tws_api_breaker = AdaptiveCircuitBreaker(
    AdaptiveCircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=30.0,
        latency_threshold_p95=0.2,  # 200ms for TWS API
        latency_threshold_p99=0.4,  # 400ms
        enable_adaptive_thresholds=True
    )
)

adaptive_llm_api_breaker = AdaptiveCircuitBreaker(
    AdaptiveCircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=60.0,
        latency_threshold_p95=2.0,   # 2s for LLM (more tolerant)
        latency_threshold_p99=5.0,   # 5s
        enable_adaptive_thresholds=True,
        adaptive_factor=1.2  # Less aggressive for LLM
    )
)
