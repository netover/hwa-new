"""
Circuit Breaker pattern implementation for TWS API reliability.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

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

        logger.debug("circuit_breaker_state_changed", old_state=old_state.value, new_state=new_state.value)

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


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""


# Global circuit breakers for TWS services
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
