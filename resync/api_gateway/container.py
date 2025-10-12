"""
Dependency injection container for Resync.  # type: ignore

This module provides a dependency injection container to manage the lifecycle
and dependencies of services, reducing tight coupling between modules.  # type: ignore
"""

from __future__ import annotations  # type: ignore

import logging  # type: ignore
from abc import abstractmethod  # type: ignore
from contextlib import asynccontextmanager  # type: ignore
from typing import Any, Protocol  # type: ignore

from resync.api_gateway.services import (IAgentService,  # type: ignore
                                         IKnowledgeService, ITWSService,
                                         ServiceFactory)
from resync.core.interfaces import (  # type: ignore[attr-defined]
    IAgentManager, IKnowledgeGraph, ITWSClient)


class IContainer(Protocol):  # type: ignore
    """Protocol for the dependency injection container."""  # type: ignore

    @abstractmethod
    def register(self, interface: type, implementation: Any) -> None:  # type: ignore
        """Register an implementation for an interface."""  # type: ignore

    @abstractmethod
    def resolve(self, interface: type) -> Any:  # type: ignore
        """Resolve an implementation for an interface."""  # type: ignore

    @abstractmethod
    async def dispose(self) -> None:  # type: ignore
        """Dispose of all managed resources."""  # type: ignore


class Container:  # type: ignore
    """Implementation of the dependency injection container."""  # type: ignore

    def __init__(self) -> None:  # type: ignore
        self._registrations: dict[type, Any] = {}  # type: ignore
        self._instances: dict[type, Any] = {}  # type: ignore
        self._logger = logging.getLogger(__name__)  # type: ignore

    def register(self, interface: type, implementation: Any) -> None:  # type: ignore
        """Register an implementation for an interface."""  # type: ignore
        self._registrations[interface] = implementation  # type: ignore
        # If implementation is a singleton, create it immediately
        if hasattr(implementation, "_singleton") and implementation._singleton:  # type: ignore
            self._instances[interface] = implementation  # type: ignore

    def register_singleton(self, interface: type, implementation: Any) -> None:  # type: ignore
        """Register a singleton implementation for an interface."""  # type: ignore
        implementation._singleton = True  # type: ignore
        self.register(interface, implementation)  # type: ignore

    def register_factory(self, interface: type, factory: Any) -> None:  # type: ignore
        """Register a factory function for an interface."""  # type: ignore
        self._registrations[interface] = factory  # type: ignore

    def resolve(self, interface: type) -> Any:  # type: ignore
        """Resolve an implementation for an interface."""  # type: ignore
        if interface in self._instances:  # type: ignore
            return self._instances[interface]  # type: ignore

        if interface not in self._registrations:  # type: ignore
            raise ValueError(f"No registration found for interface: {interface}")  # type: ignore

        implementation = self._registrations[interface]  # type: ignore

        # If it's a factory, call it to create the instance
        if callable(implementation) and not isinstance(implementation, type):  # type: ignore
            instance = implementation(self)  # type: ignore
            self._instances[interface] = instance  # type: ignore
            return instance

        # If it's a class, instantiate it
        if isinstance(implementation, type):  # type: ignore
            # Check if dependencies need to be injected
            instance = self._instantiate_with_dependencies(implementation)  # type: ignore
            self._instances[interface] = instance  # type: ignore
            return instance

        # Otherwise, return as is
        self._instances[interface] = implementation  # type: ignore
        return implementation

    def _instantiate_with_dependencies(self, cls: type) -> Any:  # type: ignore
        """Instantiate a class with its dependencies."""  # type: ignore
        # Get the constructor signature
        import inspect  # type: ignore

        sig = inspect.signature(cls.__init__)  # type: ignore

        # Prepare dependencies
        kwargs = {}  # type: ignore
        for param_name, param in sig.parameters.items():  # type: ignore
            if param_name == "self":  # type: ignore
                continue

            # Check if the parameter type is registered in our container
            if param.annotation != inspect.Parameter.empty:  # type: ignore
                try:  # type: ignore
                    dependency = self.resolve(param.annotation)  # type: ignore
                    kwargs[param_name] = dependency  # type: ignore
                except ValueError:  # type: ignore
                    # If no registration found, use the default value if available
                    if param.default != inspect.Parameter.empty:  # type: ignore
                        kwargs[param_name] = param.default  # type: ignore
                    else:  # type: ignore
                        raise ValueError(f"No registration found for dependency: {param.annotation}")  # type: ignore

        return cls(**kwargs)  # type: ignore

    async def dispose(self) -> None:  # type: ignore
        """Dispose of all managed resources."""  # type: ignore
        for instance in self._instances.values():  # type: ignore
            if hasattr(instance, "close") and callable(instance.close):  # type: ignore
                try:  # type: ignore
                    await instance.close()  # type: ignore
                except Exception as e:  # type: ignore
                    self._logger.error(f"Error disposing instance: {e}")  # type: ignore

        self._instances.clear()  # type: ignore


# Global container instance
container = Container()  # type: ignore


def setup_dependencies(tws_client: ITWSClient, agent_manager: IAgentManager, knowledge_graph: IKnowledgeGraph) -> None:  # type: ignore
    """Setup the dependency injection container with all necessary services."""  # type: ignore
    # Register core components
    container.register_singleton(ITWSClient, tws_client)  # type: ignore
    container.register_singleton(IAgentManager, agent_manager)  # type: ignore
    container.register_singleton(IKnowledgeGraph, knowledge_graph)  # type: ignore

    # Register services using the factory
    container.register_singleton(  # type: ignore
        ITWSService, ServiceFactory.create_tws_service(tws_client)  # type: ignore
    )
    container.register_singleton(  # type: ignore
        IAgentService,
        ServiceFactory.create_agent_service(agent_manager),  # type: ignore
    )
    container.register_singleton(  # type: ignore
        IKnowledgeService,
        ServiceFactory.create_knowledge_service(knowledge_graph),  # type: ignore
    )


# Context manager for container lifecycle
@asynccontextmanager
async def container_lifespan() -> Any:  # type: ignore
    """Context manager to handle container lifecycle."""  # type: ignore
    try:  # type: ignore
        yield container
    finally:  # type: ignore
        await container.dispose()  # type: ignore
