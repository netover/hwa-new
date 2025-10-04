"""
Dependency Injection Container for Resync

This module implements a hardened dependency injection container that manages
the creation and lifecycle of services in the application. It supports different
scopes (singleton and transient), health validation, and contract enforcement.

The container guarantees instance validity and includes health checks as part
of the DI contract to ensure system reliability.
"""

import asyncio
import inspect
import logging
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Protocol,
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


# --- Health Check Protocol ---
class HealthCheckable(Protocol):
    """Protocol for services that support health checks."""

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the service.

        Returns:
            Dict containing health status information.
            Must include at least a 'status' key with values: 'healthy', 'degraded', 'error'
        """
        ...


class HasHealthCheck:
    """Mixin to add health check capability to services."""

    async def health_check(self) -> Dict[str, Any]:
        """Default health check implementation."""
        return {
            "status": "healthy",
            "service": self.__class__.__name__,
            "timestamp": asyncio.get_event_loop().time(),
        }


class ServiceScope(Enum):
    """Defines the lifecycle scope of a registered service."""

    SINGLETON = auto()  # One instance per container
    TRANSIENT = auto()  # New instance each time requested


class ServiceRegistration(Generic[TInterface, TImplementation]):
    """
    Represents a hardened service registration in the container with health validation.

    Attributes:
        interface: The interface type that will be requested.
        implementation: The concrete implementation type that will be instantiated.
        scope: The lifecycle scope of the service.
        factory: Optional factory function to create the service.
        instance: Cached instance for singleton services.
        health_required: Whether health checks are required for this service.
        health_timeout: Timeout for health checks in seconds.
    """

    def __init__(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        scope: ServiceScope,
        factory: Optional[Callable[..., TImplementation]] = None,
        health_required: bool = True,
        health_timeout: float = 5.0,
    ):
        self.interface = interface
        self.implementation = implementation
        self.scope = scope
        self.factory = factory
        self.instance: Optional[TImplementation] = None
        self.health_required = health_required
        self.health_timeout = health_timeout
        self._health_check_failures = 0
        self._last_health_check = 0.0
        self._health_check_cache: Optional[Dict[str, Any]] = None
        self._health_check_cache_timeout = 30.0  # Cache health checks for 30 seconds


class DIContainer:
    """
    A lightweight dependency injection container.

    The container manages service registrations and their lifecycles,
    resolving dependencies when services are requested.
    """

    def __init__(self) -> None:
        """Initialize an empty container."""
        self._registrations: Dict[Type[Any], ServiceRegistration[Any, Any]] = {}
        logger.info("DIContainer initialized")

    def register(
        self,
        interface: Type[TInterface],
        implementation: Type[TImplementation],
        scope: ServiceScope = ServiceScope.SINGLETON,
        health_required: bool = True,
        health_timeout: float = 5.0,
    ) -> None:
        """
        Register an interface and its implementation with the container with health validation.

        Args:
            interface: The interface type that will be requested.
            implementation: The concrete implementation type that will be instantiated.
            scope: The lifecycle scope of the service (default: SINGLETON).
            health_required: Whether health checks are required for this service.
            health_timeout: Timeout for health checks in seconds.
        """
        # Validate implementation has required methods
        self._validate_implementation(interface, implementation)

        registration = ServiceRegistration(
            interface=interface,
            implementation=implementation,
            scope=scope,
            health_required=health_required,
            health_timeout=health_timeout,
        )

        self._registrations[interface] = registration
        logger.info(
            f"Registered {interface.__name__} -> {implementation.__name__} with scope {scope.name}, "
            f"health_required={health_required}"
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
            implementation=type(instance),
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
            implementation=object,  # Type doesn't matter for factory
            scope=scope,
            factory=factory,
        )
        logger.debug(
            f"Registered factory for {interface.__name__} with scope {scope.name}"
        )

    async def get(self, interface: Type[T]) -> T:
        """
        Resolve and return a validated instance of the requested interface.

        Args:
            interface: The interface type to resolve.

        Returns:
            An instance of the implementation registered for the interface.

        Raises:
            KeyError: If the interface is not registered.
            ValueError: If there's an error creating or validating the instance.
            RuntimeError: If health checks fail for the instance.
        """
        if interface not in self._registrations:
            raise KeyError(f"No registration found for {interface.__name__}")

        registration = self._registrations[interface]

        # For singletons, return the cached instance if available and healthy
        if (
            registration.scope == ServiceScope.SINGLETON
            and registration.instance is not None
        ):
            # Validate cached instance health
            if await self._is_instance_healthy(registration, registration.instance):
                return cast(T, registration.instance)
            else:
                logger.warning(
                    f"Cached instance of {interface.__name__} is unhealthy, recreating"
                )
                registration.instance = None

        # Create a new instance
        instance = await self._create_instance(registration)

        # Validate the new instance
        if not await self._is_instance_healthy(registration, instance):
            raise RuntimeError(
                f"Created instance of {interface.__name__} failed health validation"
            )

        # Cache singleton instances
        if registration.scope == ServiceScope.SINGLETON:
            registration.instance = instance

        return cast(T, instance)

    async def _create_instance(
        self, registration: ServiceRegistration[Any, Any]
    ) -> Any:
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
            return await self._instantiate_with_dependencies(
                registration.implementation
            )
        except Exception as e:
            logger.error(
                f"Error creating instance of {registration.implementation.__name__}: {e}",
                exc_info=True,
            )
            raise ValueError(
                f"Error creating instance of {registration.implementation.__name__}: {e}"
            ) from e

    async def _instantiate_with_dependencies(self, implementation: Type[Any]) -> Any:
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
                kwargs[param.name] = await self.get(param_type)
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

    def _validate_implementation(
        self, interface: Type[Any], implementation: Type[Any]
    ) -> None:
        """
        Validate that the implementation satisfies the interface contract.

        Args:
            interface: The interface type.
            implementation: The implementation type.

        Raises:
            ValueError: If validation fails.
        """
        # Check if implementation is a subclass of interface (if interface is a class)
        if inspect.isclass(interface) and not issubclass(implementation, interface):
            # Allow if it's a protocol (structural typing)
            if hasattr(interface, "__protocol__"):
                return
            raise ValueError(
                f"{implementation.__name__} does not implement {interface.__name__}"
            )

        # Additional validations can be added here
        logger.debug(
            f"Implementation validation passed for {interface.__name__} -> {implementation.__name__}"
        )

    async def _is_instance_healthy(
        self, registration: ServiceRegistration[Any, Any], instance: Any
    ) -> bool:
        """
        Check if an instance is healthy according to its registration requirements.

        Args:
            registration: The service registration.
            instance: The instance to check.

        Returns:
            True if healthy, False otherwise.
        """
        if not registration.health_required:
            return True

        try:
            # Check cache first
            current_time = asyncio.get_event_loop().time()
            if (
                registration._health_check_cache is not None
                and current_time - registration._last_health_check
                < registration._health_check_cache_timeout
            ):
                cached_status = registration._health_check_cache.get(
                    "status", "unknown"
                )
                return cached_status in ("healthy", "degraded")

            # Perform health check
            health_result = await asyncio.wait_for(
                self._perform_health_check(instance),
                timeout=registration.health_timeout,
            )

            # Cache result
            registration._health_check_cache = health_result
            registration._last_health_check = current_time

            # Reset failure count on success
            if health_result.get("status") in ("healthy", "degraded"):
                registration._health_check_failures = 0
                return True
            else:
                registration._health_check_failures += 1
                logger.warning(
                    f"Health check failed for {registration.interface.__name__}: "
                    f"{health_result.get('status', 'unknown')}"
                )
                return False

        except asyncio.TimeoutError:
            registration._health_check_failures += 1
            logger.error(f"Health check timeout for {registration.interface.__name__}")
            return False
        except Exception as e:
            registration._health_check_failures += 1
            logger.error(
                f"Health check error for {registration.interface.__name__}: {e}"
            )
            return False

    async def _perform_health_check(self, instance: Any) -> Dict[str, Any]:
        """
        Perform a health check on an instance.

        Args:
            instance: The instance to check.

        Returns:
            Health check result dictionary.
        """
        if hasattr(instance, "health_check") and callable(
            instance.health_check
        ):
            # Instance has its own health check method
            if inspect.iscoroutinefunction(instance.health_check):
                return await instance.health_check()
            else:
                # Run sync health check in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, instance.health_check)
        else:
            # Default health check
            return {
                "status": "healthy",
                "service": instance.__class__.__name__,
                "timestamp": asyncio.get_event_loop().time(),
                "message": "No specific health check implemented",
            }

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of all registered services.

        Returns:
            Dictionary with health status of all services.
        """
        status = {
            "overall_status": "healthy",
            "services": {},
            "timestamp": asyncio.get_event_loop().time(),
        }

        tasks = []
        interfaces = []

        for interface, registration in self._registrations.items():
            interfaces.append(interface)
            if registration.instance is not None:
                # Create a task to perform the health check
                task = asyncio.wait_for(
                    self._perform_health_check(registration.instance), timeout=2.0
                )
                tasks.append(task)
            else:
                # If no instance, create a placeholder result by creating a coroutine that does nothing
                async def placeholder():
                    return {"status": "not_initialized"}

                tasks.append(placeholder())

        # Run all health checks concurrently
        health_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, interface in enumerate(interfaces):
            registration = self._registrations[interface]
            health_result = health_results[i]

            service_status = {
                "interface": interface.__name__,
                "implementation": registration.implementation.__name__,
                "scope": registration.scope.name,
                "health_required": registration.health_required,
                "has_instance": registration.instance is not None,
            }

            if isinstance(health_result, Exception):
                service_status["health"] = {
                    "status": "error",
                    "error": str(health_result),
                }
                status["overall_status"] = "error"
            else:
                service_status["health"] = health_result
                if health_result.get("status") not in ("healthy", "degraded"):
                    status["overall_status"] = "degraded"

            status["services"][interface.__name__] = service_status

        return status

    def clear(self) -> None:
        """Clear all registrations and cached instances."""
        self._registrations.clear()
        logger.info("DIContainer cleared")


# --- Global Container Instance ---
# This is the default container used by the application.
# It can be replaced with a custom container if needed.
container = DIContainer()


def register_default_services():
    """Register default services with the container."""
    from resync.core.audit_queue import AsyncAuditQueue, IAuditQueue
    container.register(IAuditQueue, AsyncAuditQueue, scope=ServiceScope.SINGLETON, health_required=False)  # type: ignore[type-abstract]


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    return container

# Register AsyncAuditQueue as the implementation for IAuditQueue



def get_container() -> DIContainer:
    """Get the global DI container instance."""
    return container
