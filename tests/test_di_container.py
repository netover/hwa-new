"""
Tests for the DIContainer implementation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import pytest

from resync.core.di_container import DIContainer, ServiceScope

# --- Test Fixtures ---


@runtime_checkable
class IService(Protocol):
    """Test interface for services."""

    def get_value(self) -> str: ...


class ServiceA:
    """Test service implementation A."""

    def get_value(self) -> str:
        return "ServiceA"


class ServiceB:
    """Test service implementation B."""

    def get_value(self) -> str:
        return "ServiceB"


class ServiceWithDependency:
    """Test service with a dependency."""

    def __init__(self, dependency: IService):
        self.dependency = dependency

    def get_value(self) -> str:
        return f"ServiceWithDependency({self.dependency.get_value()})"


@pytest.fixture
def container() -> DIContainer:
    """Create a fresh DIContainer for each test."""
    return DIContainer()


# --- Tests ---


def test_register_and_get(container: DIContainer):
    """Test registering and retrieving a service."""
    # Register a service
    container.register(IService, ServiceA)

    # Get the service
    service = container.get(IService)

    # Verify the service
    assert isinstance(service, ServiceA)
    assert service.get_value() == "ServiceA"


def test_register_instance(container: DIContainer):
    """Test registering a pre-created instance."""
    # Create an instance
    instance = ServiceA()

    # Register the instance
    container.register_instance(IService, instance)

    # Get the service
    service = container.get(IService)

    # Verify it's the same instance
    assert service is instance


def test_register_factory(container: DIContainer):
    """Test registering a factory function."""
    # Register a factory
    container.register_factory(IService, lambda: ServiceB())

    # Get the service
    service = container.get(IService)

    # Verify the service
    assert isinstance(service, ServiceB)
    assert service.get_value() == "ServiceB"


def test_singleton_scope(container: DIContainer):
    """Test that singleton services return the same instance."""
    # Register a service as singleton
    container.register(IService, ServiceA, ServiceScope.SINGLETON)

    # Get the service twice
    service1 = container.get(IService)
    service2 = container.get(IService)

    # Verify they're the same instance
    assert service1 is service2


def test_transient_scope(container: DIContainer):
    """Test that transient services return different instances."""
    # Register a service as transient
    container.register(IService, ServiceA, ServiceScope.TRANSIENT)

    # Get the service twice
    service1 = container.get(IService)
    service2 = container.get(IService)

    # Verify they're different instances
    assert service1 is not service2
    # But they're both the right type
    assert isinstance(service1, ServiceA)
    assert isinstance(service2, ServiceA)


def test_dependency_resolution(container: DIContainer):
    """Test that dependencies are automatically resolved."""
    # Register the dependency
    container.register(IService, ServiceA)

    # Register the service with dependency
    container.register(ServiceWithDependency, ServiceWithDependency)

    # Get the service
    service = container.get(ServiceWithDependency)

    # Verify the service and its dependency
    assert isinstance(service, ServiceWithDependency)
    assert isinstance(service.dependency, ServiceA)
    assert service.get_value() == "ServiceWithDependency(ServiceA)"


def test_missing_service(container: DIContainer):
    """Test that getting an unregistered service raises KeyError."""
    with pytest.raises(KeyError):
        container.get(IService)


def test_missing_dependency(container: DIContainer):
    """Test that resolving a service with an unregistered dependency raises ValueError."""
    # Register the service with dependency, but not the dependency
    container.register(ServiceWithDependency, ServiceWithDependency)

    # Try to get the service
    with pytest.raises(ValueError):
        container.get(ServiceWithDependency)


def test_clear(container: DIContainer):
    """Test clearing the container."""
    # Register a service
    container.register(IService, ServiceA)

    # Verify it's there
    service = container.get(IService)
    assert isinstance(service, ServiceA)

    # Clear the container
    container.clear()

    # Verify the service is gone
    with pytest.raises(KeyError):
        container.get(IService)
