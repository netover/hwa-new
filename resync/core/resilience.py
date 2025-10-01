from __future__ import annotations

import logging
import os
from time import time as time_func
from typing import Any, Dict

import pybreaker
from pybreaker import CircuitBreaker

from resync.core.app_context import AppContext
from resync.core.security import InputSanitizer

logger = logging.getLogger(__name__)


class AdaptiveCircuitBreaker:
    """Adaptive circuit breaker with configurable thresholds and metrics."""

    def __init__(self, name: str, operation: str):
        self.name = name
        self.operation = operation
        self._metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opened_count": 0,
            "last_failure_time": None,
            "failure_streak": 0,
        }
        self._circuit_breaker = None
        self._create_circuit_breaker()

    def _create_circuit_breaker(self):
        """Create circuit breaker with configurable thresholds."""
        fail_max = InputSanitizer.sanitize_environment_value(
            f"CIRCUIT_BREAKER_{self.operation.upper()}_FAIL_MAX",
            os.getenv(f"CIRCUIT_BREAKER_{self.operation.upper()}_FAIL_MAX", "5"),
            int,
        )
        reset_timeout = InputSanitizer.sanitize_environment_value(
            f"CIRCUIT_BREAKER_{self.operation.upper()}_RESET_TIMEOUT",
            os.getenv(f"CIRCUIT_BREAKER_{self.operation.upper()}_RESET_TIMEOUT", "60"),
            int,
        )

        fail_max = max(1, min(fail_max, 100))  # 1-100
        reset_timeout = max(10, min(reset_timeout, 3600))  # 10 seconds to 1 hour

        self._circuit_breaker = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            name=f"{self.name}_{self.operation}",
            listeners=[self],
        )

        logger.info(
            f"Created adaptive circuit breaker for {self.operation}",
            extra={
                "correlation_id": AppContext.get_correlation_id(),
                "component": "circuit_breaker",
                "operation": "create",
                "fail_max": fail_max,
                "reset_timeout": reset_timeout,
            },
        )

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        correlation_id = AppContext.get_correlation_id()
        self._metrics["total_calls"] += 1

        try:
            result = await self._circuit_breaker.call(func, *args, **kwargs)
            self._metrics["successful_calls"] += 1
            self._metrics["failure_streak"] = 0
            return result

        except pybreaker.CircuitBreakerError as e:
            self._metrics["circuit_opened_count"] += 1
            logger.warning(
                f"Circuit breaker opened for {self.operation}",
                extra={
                    "correlation_id": correlation_id,
                    "component": "circuit_breaker",
                    "operation": "circuit_opened",
                    "error": e,
                    "opened_count": self._metrics["circuit_opened_count"],
                },
            )
            raise

        except Exception as e:
            self._metrics["failed_calls"] += 1
            self._metrics["failure_streak"] += 1
            self._metrics["last_failure_time"] = time_func()
            logger.warning(
                f"Circuit breaker call failed for {self.operation}",
                extra={
                    "correlation_id": correlation_id,
                    "component": "circuit_breaker",
                    "operation": "call_failed",
                    "error": e,
                    "failure_streak": self._metrics["failure_streak"],
                },
            )
            raise

    def get_success_rate(self) -> float:
        """Calculate success rate."""
        total = self._metrics["total_calls"]
        if total == 0:
            return 1.0
        return self._metrics["successful_calls"] / total

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            **self._metrics,
            "success_rate": self.get_success_rate(),
            "circuit_state": self._circuit_breaker.current_state
            if self._circuit_breaker
            else "unknown",
            "fail_max": self._circuit_breaker.fail_max if self._circuit_breaker else 0,
            "reset_timeout": self._circuit_breaker.reset_timeout
            if self._circuit_breaker
            else 0,
        }

    def state_change(self, cb, old_state, new_state):
        """Called when circuit breaker state changes."""
        logger.info(
            f"Circuit breaker state changed for {self.operation}: {old_state.name} -> {new_state.name}",
            extra={
                "correlation_id": AppContext.get_correlation_id(),
                "component": "circuit_breaker",
                "operation": "state_change",
                "old_state": old_state.name,
                "new_state": new_state.name,
            },
        )

    def before_call(self, cb, func, *args, **kwargs):
        """Called before the circuit breaker is called."""
        pass

    def failure(self, cb, exc):
        """Called on failure."""
        pass  # Already handled in call method

    def success(self, cb):
        """Called on success."""
        pass  # Already handled in call method


class CircuitBreakerManager:
    """Manager for multiple adaptive circuit breakers."""

    def __init__(self):
        self._breakers: Dict[str, AdaptiveCircuitBreaker] = {}

    def get_breaker(self, operation: str) -> AdaptiveCircuitBreaker:
        """Get or create circuit breaker for operation."""
        if operation not in self._breakers:
            self._breakers[operation] = AdaptiveCircuitBreaker(
                name="adaptive_cb", operation=operation
            )
        return self._breakers[operation]

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        return {
            operation: breaker.get_metrics()
            for operation, breaker in self._breakers.items()
        }


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()

# Legacy circuit breaker for backward compatibility
redis_circuit_breaker = circuit_breaker_manager.get_breaker("tws_client")._circuit_breaker