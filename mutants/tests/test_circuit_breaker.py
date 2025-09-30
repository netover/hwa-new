"""
Tests for Adaptive Circuit Breaker functionality.
"""

import pytest
import asyncio
from resync.main import CircuitBreakerManager


class TestAdaptiveCircuitBreaker:
    """Test cases for AdaptiveCircuitBreaker."""

    def test_circuit_breaker_creation(self):
        """Test circuit breaker manager and breaker creation."""
        manager = CircuitBreakerManager()

        # Get breaker for operation
        breaker = manager.get_breaker("test_operation")

        # Verify breaker was created
        assert breaker is not None
        assert breaker.operation == "test_operation"

        # Get same breaker again (should return cached)
        breaker2 = manager.get_breaker("test_operation")
        assert breaker is breaker2

    def test_circuit_breaker_metrics(self):
        """Test circuit breaker metrics collection."""
        manager = CircuitBreakerManager()
        breaker = manager.get_breaker("metrics_test")

        # Check initial metrics
        metrics = breaker.get_metrics()
        assert metrics["total_calls"] == 0
        assert metrics["successful_calls"] == 0
        assert metrics["failed_calls"] == 0
        assert metrics["success_rate"] == 1.0  # No calls yet

    @pytest.mark.asyncio
    async def test_circuit_breaker_successful_call(self):
        """Test successful circuit breaker call."""
        manager = CircuitBreakerManager()
        breaker = manager.get_breaker("success_test")

        # Mock successful function
        async def success_func():
            return "success"

        # Execute call
        result = await breaker.call(success_func)

        # Verify result
        assert result == "success"

        # Check metrics
        metrics = breaker.get_metrics()
        assert metrics["total_calls"] == 1
        assert metrics["successful_calls"] == 1
        assert metrics["failed_calls"] == 0
        assert metrics["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_circuit_breaker_failed_call(self):
        """Test failed circuit breaker call."""
        manager = CircuitBreakerManager()
        breaker = manager.get_breaker("failure_test")

        # Mock failing function
        async def failure_func():
            raise ValueError("Test failure")

        # Execute call (should raise)
        with pytest.raises(ValueError, match="Test failure"):
            await breaker.call(failure_func)

        # Check metrics
        metrics = breaker.get_metrics()
        assert metrics["total_calls"] == 1
        assert metrics["successful_calls"] == 0
        assert metrics["failed_calls"] == 1
        assert metrics["success_rate"] == 0.0
        assert metrics["failure_streak"] == 1

    def test_circuit_breaker_manager_metrics(self):
        """Test circuit breaker manager metrics collection."""
        manager = CircuitBreakerManager()

        # Create multiple breakers
        breaker1 = manager.get_breaker("op1")
        breaker2 = manager.get_breaker("op2")

        # Get all metrics
        all_metrics = manager.get_all_metrics()

        assert "op1" in all_metrics
        assert "op2" in all_metrics
        assert len(all_metrics) == 2
