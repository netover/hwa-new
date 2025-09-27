"""
Dependency Injection Container for Resync

This module implements a lightweight dependency injection container that manages
the creation and lifecycle of services in the application. It supports different
scopes (singleton and transient) and allows for the registration of interfaces
and their implementations.

The container is designed to be used with FastAPI's dependency injection system
but can also be used standalone.
"""

import inspect
import logging
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    cast,
    get_type_hints,
)

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- Type Variables ---
T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")


class ServiceScope(Enum):
    """Defines the lifecycle scope of a registered service."""

    SINGLETON = auto()  # One instance per container
    TRANSIENT = auto()  # New instance each time requested


class ServiceRegistration(Generic[TInterface, TImplementation]):
    """
    Represents a service registration in the container.

    Attributes:
        interface: The interface type that will be requested.
        implementation: The concrete implementation type that will be instantiated.
        scope: The lifecycle scope of the service.
        factory: Optional factory function to create the service.
        instance: Cached instance for singleton services.
    """

    def __init__(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        scope: ServiceScope,
        factory: Optional[Callable[..., TImplementation]] = None,
    ):
        self.interface = interface
        self.implementation = implementation
        self.scope = scope
        self.factory = factory
        self.instance: Optional[TImplementation] = None


class DIContainer:
    """
    A lightweight dependency injection container.

    The container manages service registrations and their lifecycles,
    resolving dependencies when services are requested.
    """

    def __init__(self):
        """Initialize an empty container."""
        self._registrations: Dict[Type[Any], ServiceRegistration[Any, Any]] = {}
        logger.info("DIContainer initialized")

    def register(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        scope: ServiceScope = ServiceScope.SINGLETON,
    ) -> None:
        """
        Register an interface and its implementation with the container.

        Args:
            interface: The interface type that will be requested.
            implementation: The concrete implementation type that will be instantiated.
            scope: The lifecycle scope of the service (default: SINGLETON).
        """
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            scope=scope,
        )
        logger.debug(
            f"Registered {interface.__name__} -> {implementation.__name__} with scope {scope.name}"
        )

    def register_instance(
        self, interface: Type[TInterface], instance: TImplementation
    ) -> None:
        """
        Register a pre-created instance with the container.

        Args:
            interface: The interface type that will be requested.
            instance: The pre-created instance to return when the interface is requested.
        """
        registration = ServiceRegistration(
            interface=interface,
            implementation=cast(Type[TImplementation], type(instance)),
            scope=ServiceScope.SINGLETON,
        )
        registration.instance = instance
        self._registrations[interface] = registration
        logger.debug(f"Registered instance of {interface.__name__}")

    def register_factory(
        self,
        interface: Type[TInterface],
        factory: Callable[..., TImplementation],
        scope: ServiceScope = ServiceScope.SINGLETON,
    ) -> None:
        """
        Register a factory function to create instances of a service.

        Args:
            interface: The interface type that will be requested.
            factory: A function that creates instances of the implementation.
            scope: The lifecycle scope of the service (default: SINGLETON).
        """
        self._registrations[interface] = ServiceRegistration(
            interface=interface,
            implementation=cast(
                Type[TImplementation], object
            ),  # Type doesn't matter for factory
            scope=scope,
            factory=factory,
        )
        logger.debug(
            f"Registered factory for {interface.__name__} with scope {scope.name}"
        )

    def get(self, interface: Type[T]) -> T:
        """
        Resolve and return an instance of the requested interface.

        Args:
            interface: The interface type to resolve.

        Returns:
            An instance of the implementation registered for the interface.

        Raises:
            KeyError: If the interface is not registered.
            ValueError: If there's an error creating the instance.
        """
        if interface not in self._registrations:
            raise KeyError(f"No registration found for {interface.__name__}")

        registration = self._registrations[interface]

        # For singletons, return the cached instance if available
        if (
            registration.scope == ServiceScope.SINGLETON
            and registration.instance is not None
        ):
            return cast(T, registration.instance)

        # Create a new instance
        instance = self._create_instance(registration)

        # Cache singleton instances
        if registration.scope == ServiceScope.SINGLETON:
            registration.instance = instance

        return cast(T, instance)

    def _create_instance(self, registration: ServiceRegistration[Any, Any]) -> Any:
        """
        Create an instance of the implementation based on the registration.

        Args:
            registration: The service registration.

        Returns:
            An instance of the implementation.

        Raises:
            ValueError: If there's an error creating the instance.
        """
        try:
            # If a factory is provided, use it
            if registration.factory:
                return registration.factory()

            # Otherwise, try to instantiate the implementation with its dependencies
            return self._instantiate_with_dependencies(registration.implementation)
        except Exception as e:
            logger.error(
                f"Error creating instance of {registration.implementation.__name__}: {e}",
                exc_info=True,
            )
            raise ValueError(
                f"Error creating instance of {registration.implementation.__name__}: {e}"
            ) from e

    def _instantiate_with_dependencies(self, implementation: Type[Any]) -> Any:
        """
        Instantiate an implementation, resolving its constructor dependencies.

        Args:
            implementation: The implementation type to instantiate.

        Returns:
            An instance of the implementation.
        """
        # Get the constructor signature
        signature = inspect.signature(implementation.__init__)

        # Skip self parameter
        parameters = list(signature.parameters.values())[1:]

        # Get type hints for constructor parameters
        type_hints = get_type_hints(implementation.__init__)

        # Build arguments for the constructor
        kwargs = {}
        for param in parameters:
            # Skip *args and **kwargs
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            # Get parameter type
            param_type = type_hints.get(param.name, Any)

            # Try to resolve the parameter from the container
            try:
                kwargs[param.name] = self.get(param_type)
            except KeyError:
                # If the parameter has a default value, use it
                if param.default is not param.empty:
                    kwargs[param.name] = param.default
                else:
                    # Otherwise, raise an error
                    raise ValueError(
                        f"Cannot resolve parameter '{param.name}' of type '{param_type}' "
                        f"for {implementation.__name__}.__init__"
                    )

        # Create the instance
        return implementation(**kwargs)

    def clear(self) -> None:
        """Clear all registrations and cached instances."""
        self._registrations.clear()
        logger.info("DIContainer cleared")


# --- Global Container Instance ---
# This is the default container used by the application.
# It can be replaced with a custom container if needed.
container = DIContainer()
