import pytest
from typing import Protocol
from typing_extensions import runtime_checkable
from resync.core.di_container import DIContainer, ServiceScope


# Define a simple protocol for testing
@runtime_checkable
class TestProtocol(Protocol):
    def do_something(self) -> str:
        ...


# Define compliant and non-compliant implementations
class CompliantImplementation:
    def do_something(self) -> str:
        return "Compliant implementation"


class NonCompliantImplementation:
    def do_other_thing(self) -> str:
        return "Non-compliant implementation"


# Define a protocol with non-method attributes
@runtime_checkable
class ComplexProtocol(Protocol):
    name: str
    
    def process(self) -> None:
        ...


class ComplexImplementation:
    name: str = "test"
    
    def process(self) -> None:
        pass


def test_strict_mode_enabled():
    """Test that strict mode can be enabled."""
    container = DIContainer(strict_mode=True)
    assert container.strict_mode is True


def test_strict_mode_disabled():
    """Test that strict mode can be disabled."""
    container = DIContainer(strict_mode=False)
    assert container.strict_mode is False


def test_strict_mode_runtime_change():
    """Test that strict mode can be changed at runtime."""
    container = DIContainer(strict_mode=False)
    assert container.strict_mode is False
    
    container.strict_mode = True
    assert container.strict_mode is True


def test_protocol_validation_compliant():
    """Test that compliant protocol implementations pass validation."""
    container = DIContainer()
    
    # Should not raise an exception
    container._validate_implementation(TestProtocol, CompliantImplementation)


def test_protocol_validation_non_compliant_warning():
    """Test that non-compliant protocol implementations generate warnings in non-strict mode."""
    container = DIContainer(strict_mode=False)
    
    # Should not raise an exception but should log a warning
    container._validate_implementation(TestProtocol, NonCompliantImplementation)


def test_protocol_validation_non_compliant_strict():
    """Test that non-compliant protocol implementations raise exceptions in strict mode."""
    container = DIContainer(strict_mode=True)
    
    # Should raise an exception
    with pytest.raises(ValueError):
        container._validate_implementation(TestProtocol, NonCompliantImplementation)


def test_complex_protocol_validation():
    """Test validation of protocols with attributes."""
    container = DIContainer()
    
    # Should not raise an exception
    container._validate_implementation(ComplexProtocol, ComplexImplementation)


def test_register_factory_without_hint_non_strict():
    """Test registering factory without type hint in non-strict mode."""
    container = DIContainer(strict_mode=False)
    
    def factory():
        return CompliantImplementation()
    
    # Should not raise an exception
    container.register_factory(TestProtocol, factory)


def test_register_factory_without_hint_strict():
    """Test registering factory without type hint in strict mode raises exception."""
    container = DIContainer(strict_mode=True)
    
    def factory():
        return CompliantImplementation()
    
    # Should raise an exception
    with pytest.raises(ValueError):
        container.register_factory(TestProtocol, factory)


def test_register_factory_with_hint():
    """Test registering factory with type hint."""
    container = DIContainer()
    
    def factory():
        return CompliantImplementation()
    
    # Should not raise an exception
    container.register_factory(
        TestProtocol, factory, implementation_type_hint=CompliantImplementation
    )


def test_register_instance_validation():
    """Test that register_instance validates the instance."""
    container = DIContainer()
    
    instance = CompliantImplementation()
    
    # Should not raise an exception
    container.register_instance(TestProtocol, instance)


def test_register_instance_validation_strict():
    """Test that register_instance validates the instance in strict mode."""
    container = DIContainer(strict_mode=True)
    
    instance = CompliantImplementation()
    
    # Should not raise an exception
    container.register_instance(TestProtocol, instance)


def test_get_registration_audit():
    """Test getting registration audit information."""
    container = DIContainer()
    
    # Add some registrations
    container.register(TestProtocol, CompliantImplementation)
    
    def factory():
        return CompliantImplementation()
    
    container.register_factory(
        ComplexProtocol, factory, implementation_type_hint=ComplexImplementation
    )
    
    # Get audit information
    audit = container.get_registration_audit()
    
    assert audit["total_registrations"] == 2
    assert len(audit["registrations"]) == 2
    assert audit["strict_mode"] is False
    
    # Check that all registrations are included
    interface_names = [reg["interface"] for reg in audit["registrations"]]
    assert "TestProtocol" in interface_names
    assert "ComplexProtocol" in interface_names