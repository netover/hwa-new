"""
FastAPI Integration for Dependency Injection

This module provides utilities for integrating the DIContainer with FastAPI's
dependency injection system. It includes functions for creating FastAPI dependencies
that resolve services from the container.
"""

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, Type, get_type_hints, TypeVar, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from resync.core.agent_manager import AgentManager
from resync.core.audit_queue import AsyncAuditQueue
from resync.core.connection_manager import ConnectionManager
from resync.core.di_container import DIContainer, ServiceScope, container
from resync.core.file_ingestor import create_file_ingestor
from resync.core.interfaces import (
    IAgentManager,
    IAuditQueue,
    IConnectionManager,
    IFileIngestor,
    IKnowledgeGraph,
    ITWSClient,
)
from resync.core.knowledge_graph import AsyncKnowledgeGraph
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- Type Variables ---
T = TypeVar("T")


def get_tws_client_factory():
    """
    Factory function to create a TWS client based on settings.

    Returns:
        Either a real OptimizedTWSClient or a MockTWSClient.
    """
    if settings.TWS_MOCK_MODE:
        logger.info("TWS_MOCK_MODE is enabled. Creating MockTWSClient.")
        return MockTWSClient()
    else:
        logger.info("Creating OptimizedTWSClient.")
        return OptimizedTWSClient(
            hostname=settings.TWS_HOST,
            port=settings.TWS_PORT,
            username=settings.TWS_USER,
            password=settings.TWS_PASSWORD,
            engine_name=settings.TWS_ENGINE_NAME,
            engine_owner=settings.TWS_ENGINE_OWNER,
        )


def configure_container(app_container: DIContainer = container) -> DIContainer:
    """
    Configure the DI container with all service registrations.

    Args:
        app_container: The container to configure (default: global container).

    Returns:
        The configured container.
    """
    # Register interfaces and implementations
    app_container.register(IAgentManager, AgentManager, ServiceScope.SINGLETON)
    app_container.register(
        IConnectionManager, ConnectionManager, ServiceScope.SINGLETON
    )
    app_container.register(IKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON)
    app_container.register(IAuditQueue, AsyncAuditQueue, ServiceScope.SINGLETON)

    # Register TWS client with factory
    app_container.register_factory(
        ITWSClient, get_tws_client_factory, ServiceScope.SINGLETON
    )

    # Register FileIngestor - depends on KnowledgeGraph
    # Using a factory function to ensure dependencies are properly resolved
    def file_ingestor_factory():
        knowledge_graph = app_container.get(IKnowledgeGraph)
        return create_file_ingestor(knowledge_graph)

    app_container.register_factory(
        IFileIngestor, file_ingestor_factory, ServiceScope.SINGLETON
    )

    # Register concrete types (for when the concrete type is requested directly)
    app_container.register(AgentManager, AgentManager, ServiceScope.SINGLETON)
    app_container.register(ConnectionManager, ConnectionManager, ServiceScope.SINGLETON)
    app_container.register(
        AsyncKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON
    )
    app_container.register(AsyncAuditQueue, AsyncAuditQueue, ServiceScope.SINGLETON)
    app_container.register_factory(
        OptimizedTWSClient, get_tws_client_factory, ServiceScope.SINGLETON
    )

    logger.info("DI container configured with all service registrations")
    return app_container


def get_service(service_type: Type[T]) -> Callable[[], T]:
    """
    Create a FastAPI dependency that resolves a service from the container.

    Args:
        service_type: The type of service to resolve.

    Returns:
        A callable that resolves the service from the container.
    """

    def _get_service() -> T:
        return container.get(service_type)

    # Set the return annotation for FastAPI to use
    _get_service.__annotations__ = {"return": service_type}
    return _get_service


# Create specific dependencies for common services
get_agent_manager = get_service(IAgentManager)
get_connection_manager = get_service(IConnectionManager)
get_knowledge_graph = get_service(IKnowledgeGraph)
get_audit_queue = get_service(IAuditQueue)
get_tws_client = get_service(ITWSClient)
get_file_ingestor = get_service(IFileIngestor)


class DIMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures the DI container is properly initialized and
    available for each request.
    """

    def __init__(self, app: FastAPI, container_instance: DIContainer = container):
        """
        Initialize the middleware with the application and container.

        Args:
            app: The FastAPI application.
            container_instance: The DI container to use.
        """
        super().__init__(app)
        self.container = container_instance
        logger.info("DIMiddleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and attach the container to it.

        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.

        Returns:
            The response from the next handler.
        """
        # Attach the container to the request state
        request.state.container = self.container

        # Continue processing the request
        response = await call_next(request)
        return response


def inject_container(
    app: FastAPI, container_instance: Optional[DIContainer] = None
) -> None:
    """
    Configure the application to use the DI container.

    This function:
    1. Configures the container with all service registrations
    2. Adds the DIMiddleware to the application

    Args:
        app: The FastAPI application.
        container_instance: The DI container to use (default: global container).
    """
    # Use the provided container or the global one
    container_to_use = container_instance or container

    # Configure the container
    configure_container(container_to_use)

    # Add the middleware
    app.add_middleware(DIMiddleware, container_instance=container_to_use)

    logger.info("DI container injected into FastAPI application")


def with_injection(func: Callable) -> Callable:
    """
    Decorator that injects dependencies into a function from the container.

    This decorator inspects the function's signature and resolves dependencies
    from the container based on type annotations. It now correctly handles
    both synchronous and asynchronous functions.

    Args:
        func: The function to inject dependencies into.

    Returns:
        A wrapper function that resolves dependencies from the container.
    """
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())
    type_hints = get_type_hints(func)

    def inject_dependencies(kwargs: Dict[str, Any]) -> None:
        """Helper to inject dependencies into kwargs."""
        for param in parameters:
            if param.name in kwargs:
                continue
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            param_type = type_hints.get(param.name, Any)
            try:
                kwargs[param.name] = container.get(param_type)
            except KeyError:
                if param.default is not param.empty:
                    kwargs[param.name] = param.default

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            inject_dependencies(kwargs)
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            inject_dependencies(kwargs)
            return func(*args, **kwargs)
        return sync_wrapper
