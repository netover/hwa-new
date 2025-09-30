from __future__ import annotations

import logging
from typing import Any, Dict

from resync.core.circuit_breaker import CircuitBreaker
from resync.core.interfaces import ICircuitBreaker

logger = logging.getLogger(__name__)


class CircuitBreakerManager:
    """Manager for multiple adaptive circuit breakers."""

    def __init__(self):
        self._breakers: Dict[str, ICircuitBreaker] = {}

    def get_breaker(self, operation: str) -> ICircuitBreaker:
        """Get or create circuit breaker for operation."""
        if operation not in self._breakers:
            # Note: In a real scenario, the config would be more dynamic
            from resync.core.circuit_breaker import CircuitBreakerConfig
            self._breakers[operation] = CircuitBreaker(
                CircuitBreakerConfig()
            )
            logger.info(f"Created new circuit breaker for operation: {operation}")
        return self._breakers[operation]

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        return {
            operation: breaker.get_stats()
            for operation, breaker in self._breakers.items()
        }