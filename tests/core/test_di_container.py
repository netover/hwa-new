"""
Tests for hardened DI container functionality.
"""

import pytest
from typing import Protocol
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


class ServiceProtocol(Protocol):
    """Protocol to test protocol validation."""
    
    def do_something(self) -> str: ...


class ValidProtocolImplementation:
    """A class that properly implements the protocol."""
    
    def do_something(self) -> str:
        return "something done"


class InvalidProtocolImplementation:
    """A class that does not implement the protocol."""
    pass


class TestDIContainerHardening:
    """Test cases for hardened DI container."""

    async def test_container_health_validation(self):
        """Test container health validation for services."""
        container = DIContainer()

        # Register healthy service
        container.register(
            MockService, MockService, scope=ServiceScope.SINGLETON, health_required=True
        )

        # Register service with health disabled
        container.register(
            FailingService,
            FailingService,
            scope=ServiceScope.SINGLETON,
            health_required=False,
        )

        # Get healthy service
        healthy_instance = await container.get(MockService)
        assert isinstance(healthy_instance, MockService)
        assert healthy_instance.value == "default"

        # Get service with health disabled
        failing_instance = await container.get(FailingService)
        assert isinstance(failing_instance, FailingService)

    async def test_container_health_status(self):
        """Test container health status reporting."""
        container = DIContainer()

        # Register a service
        container.register(MockService, MockService, scope=ServiceScope.SINGLETON)
        # We need to get the service first to have an instance
        await container.get(MockService)

        # Get health status
        health_status = await container.get_health_status()

        assert "overall_status" in health_status
        assert "services" in health_status
        assert "MockService" in health_status["services"]

        service_status = health_status["services"]["MockService"]
        assert service_status["interface"] == "MockService"
        assert service_status["scope"] == "SINGLETON"
        assert service_status["health_required"] is True
        assert service_status["health"]["status"] == "healthy"

    async def test_invalid_implementation_validation(self):
        """Test implementation validation."""
        container = DIContainer()

        # This should work (class registration)
        container.register(str, str, scope=ServiceScope.TRANSIENT, health_required=False)

        # Get instance
        instance = await container.get(str)
        assert instance == ""

    def test_service_registration_validation(self):
        """Test service registration parameters."""
        container = DIContainer()

        # Register with custom health timeout
        container.register(
            MockService,
            MockService,
            scope=ServiceScope.SINGLETON,
            health_required=True,
            health_timeout=10.0,
        )

        # Verify registration
        registration = container._registrations[MockService]
        assert registration.health_required is True
        assert registration.health_timeout == 10.0

    def test_validate_implementation_protocol_scenarios(self):
        """Test _validate_implementation method with various protocol scenarios."""
        container = DIContainer()
        
        # Test valid protocol implementation
        container._validate_implementation(ServiceProtocol, ValidProtocolImplementation)
        
        # Test invalid protocol implementation - should raise ValueError
        with pytest.raises(ValueError, match="does not implement required methods"):
            container._validate_implementation(ServiceProtocol, InvalidProtocolImplementation)

    def test_strict_mode_validation_with_exception_raising(self):
        """Test strict mode validation with exception raising."""
        # Test normal mode doesn't raise for valid registration
        container = DIContainer(strict_mode=False)
        container.register(str, str)
        
        # Test strict mode with factory registration without type hint - should raise
        container_strict = DIContainer(strict_mode=True)
        with pytest.raises(ValueError, match="Strict mode requires explicit implementation_type_hint"):
            container_strict.register_factory(str, lambda: "test")
        
        # Test strict mode with factory registration with type hint - should work
        container_strict.register_factory(str, lambda: "test", implementation_type_hint=str)
        assert container_strict._registrations[str].implementation == str

    def test_registration_auditing_functionality(self):
        """Test registration auditing functionality."""
        container = DIContainer()
        
        # Register a service and verify audit logging
        container.register(MockService, MockService, scope=ServiceScope.SINGLETON)
        
        # Verify registration exists
        assert MockService in container._registrations
        
        # Get registration audit
        audit_info = container.get_registration_audit()
        
        assert audit_info["total_registrations"] == 1
        assert audit_info["registrations"][0]["interface"] == "MockService"
        assert audit_info["registrations"][0]["implementation"] == "MockService"
        assert audit_info["registrations"][0]["scope"] == "SINGLETON"
        assert audit_info["strict_mode"] is False

    def test_factory_registration_with_type_hints_validation(self):
        """Test factory registration with type hints validation."""
        container = DIContainer()
        
        # Test with valid type hint
        container.register_factory(
            str, 
            lambda: "test", 
            implementation_type_hint=str
        )
        
        # Verify registration
        assert str in container._registrations
        registration = container._registrations[str]
        assert registration.implementation == str
        assert registration.factory is not None
        
        # Create an instance using the factory
        instance = registration.factory()
        assert instance == "test"
