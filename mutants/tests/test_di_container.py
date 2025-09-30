"""
Tests for hardened DI container functionality.
"""

import pytest
from resync.core.di_container import DIContainer, ServiceScope


class MockService:
    """Mock service for testing."""
    def __init__(self, value: str = "default"):
        self.value = value

    async def health_check(self):
        """Mock health check."""
        return {"status": "healthy", "service": "MockService", "value": self.value}


class FailingService:
    """Mock service that fails health checks."""
    async def health_check(self):
        """Mock failing health check."""
        return {"status": "error", "service": "FailingService"}


class TestDIContainerHardening:
    """Test cases for hardened DI container."""

    def test_container_health_validation(self):
        """Test container health validation for services."""
        container = DIContainer()

        # Register healthy service
        container.register(MockService, MockService, scope=ServiceScope.SINGLETON, health_required=True)

        # Register service with health disabled
        container.register(FailingService, FailingService, scope=ServiceScope.SINGLETON, health_required=False)

        # Get healthy service
        healthy_instance = container.get(MockService)
        assert isinstance(healthy_instance, MockService)
        assert healthy_instance.value == "default"

        # Get service with health disabled
        failing_instance = container.get(FailingService)
        assert isinstance(failing_instance, FailingService)

    def test_container_health_status(self):
        """Test container health status reporting."""
        container = DIContainer()

        # Register a service
        container.register(MockService, MockService, scope=ServiceScope.SINGLETON)

        # Get health status
        health_status = container.get_health_status()

        assert "overall_status" in health_status
        assert "services" in health_status
        assert "MockService" in health_status["services"]

        service_status = health_status["services"]["MockService"]
        assert service_status["interface"] == "MockService"
        assert service_status["scope"] == "SINGLETON"
        assert service_status["health_required"] is True

    def test_invalid_implementation_validation(self):
        """Test implementation validation."""
        container = DIContainer()

        # This should work (class registration)
        container.register(str, str, scope=ServiceScope.TRANSIENT)

        # Get instance
        instance = container.get(str)
        assert instance == ""

    def test_service_registration_validation(self):
        """Test service registration parameters."""
        container = DIContainer()

        # Register with custom health timeout
        container.register(
            MockService, MockService,
            scope=ServiceScope.SINGLETON,
            health_required=True,
            health_timeout=10.0
        )

        # Verify registration
        registration = container._registrations[MockService]
        assert registration.health_required is True
        assert registration.health_timeout == 10.0
