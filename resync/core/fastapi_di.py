"""
FastAPI Integration for Dependency Injection

This module provides utilities for integrating the DIContainer with FastAPI's
dependency injection system. It includes functions for creating FastAPI dependencies
that resolve services from the container.
"""

import inspect
import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from resync.core.agent_manager import AgentManager
from resync.core.audit_queue import AsyncAuditQueue
from resync.core.connection_manager import ConnectionManager
from resync.core.di_container import DIContainer, ServiceScope
from resync.core.file_ingestor import create_file_ingestor
from resync.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from resync.core.circuit_breaker_manager import CircuitBreakerManager
from resync.core.interfaces import (
    IAgentManager,
    IAuditQueue,
    ICircuitBreaker,
    ICircuitBreakerManager,
    IConnectionManager,
    IFileIngestor,
    IKnowledgeGraph,
    ILLMCostMonitor,
    ITWSClient,
    ITWSMonitor,
)
from resync.core.knowledge_graph import AsyncKnowledgeGraph
from resync.core.llm_monitor import LLMCostMonitor
from resync.core.tws_monitor import TWSMonitor
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
            hostname=settings.TWS_HOSTNAME,
            port=settings.TWS_PORT,
            username=settings.TWS_USERNAME,
            password=settings.TWS_PASSWORD,
            engine_name=settings.TWS_ENGINE_NAME,
            engine_owner=settings.TWS_ENGINE_OWNER,
        )


def configure_container(app_container: DIContainer) -> DIContainer:
    """
    Configure the DI container with all service registrations.

    This function is the single source of truth for defining how services
    are created and what their dependencies are.

    Args:
        app_container: The container instance to configure.

    Returns:
        The configured container.
    """
    # --- Service Factories ---

    # Factory for TWS Client (handles mock vs. real client)
    app_container.register_factory(
        ITWSClient, get_tws_client_factory, ServiceScope.SINGLETON
    )

    # Factory for AgentManager (depends on ITWSClient)
    def agent_manager_factory() -> AgentManager:
        tws_client = app_container.get(ITWSClient)
        return AgentManager(tws_client=tws_client)

    app_container.register_factory(
        IAgentManager, agent_manager_factory, ServiceScope.SINGLETON
    )

    # Factory for FileIngestor (depends on IKnowledgeGraph)
    def file_ingestor_factory() -> IFileIngestor:
        knowledge_graph = app_container.get(IKnowledgeGraph)
        return create_file_ingestor(knowledge_graph)

    app_container.register_factory(
        IFileIngestor, file_ingestor_factory, ServiceScope.SINGLETON
    )

    # Factory for TWSMonitor (depends on circuit breakers and cost monitor)
    def tws_monitor_factory() -> ITWSMonitor:
        # Instantiate dependencies required by TWSMonitor
        api_breaker = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30.0)
        )
        job_status_breaker = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=3, recovery_timeout=15.0)
        )
        cost_monitor = app_container.get(ILLMCostMonitor)
        return TWSMonitor(
            api_breaker=api_breaker,
            job_status_breaker=job_status_breaker,
            cost_monitor=cost_monitor,
        )

    app_container.register_factory(
        ITWSMonitor, tws_monitor_factory, ServiceScope.SINGLETON
    )

    # --- Direct Registrations (services with no complex dependencies) ---
    app_container.register(
        IConnectionManager, ConnectionManager, ServiceScope.SINGLETON
    )
    app_container.register(IKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON)
    app_container.register(IAuditQueue, AsyncAuditQueue, ServiceScope.SINGLETON)
    app_container.register(ILLMCostMonitor, LLMCostMonitor, ServiceScope.SINGLETON)
    app_container.register(ICircuitBreakerManager, CircuitBreakerManager, ServiceScope.SINGLETON)


    # --- Concrete Type Registrations (for when a concrete type is requested) ---
    # This allows injecting the concrete class itself, e.g., for type checking
    # or when a specific implementation method is needed.
    app_container.register_factory(AgentManager, agent_manager_factory, ServiceScope.SINGLETON)
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


def get_service(service_type: Type[T]) -> Callable[[Request], T]:
    """
    Create a FastAPI dependency that resolves a service from the container
    stored in the request state.

    Args:
        service_type: The type of service to resolve.

    Returns:
        A callable that FastAPI can use as a dependency.
    """

    def _get_service(request: Request) -> T:
        """
        Resolves and returns a service instance from the container attached to
        the request.
        """
        try:
            return request.state.container.get(service_type)
        except AttributeError:
            # This would indicate a severe configuration error
            # where the middleware is not running.
            logger.critical("DI container not found in request state. Is DIMiddleware configured?")
            raise RuntimeError("DI container not found in request state.")

    return _get_service


# Create specific dependencies for common services
get_agent_manager: Callable[[Request], IAgentManager] = get_service(IAgentManager)
get_connection_manager: Callable[[Request], IConnectionManager] = get_service(IConnectionManager)
get_knowledge_graph: Callable[[Request], IKnowledgeGraph] = get_service(IKnowledgeGraph)
get_audit_queue: Callable[[Request], IAuditQueue] = get_service(IAuditQueue)
get_tws_client: Callable[[Request], ITWSClient] = get_service(ITWSClient)
get_file_ingestor: Callable[[Request], IFileIngestor] = get_service(IFileIngestor)
get_tws_monitor: Callable[[Request], ITWSMonitor] = get_service(ITWSMonitor)


class DIMiddleware(BaseHTTPMiddleware):
    """
    Middleware that attaches the application's DI container to each request's state.
    """

    def __init__(self, app: FastAPI, container_instance: DIContainer):
        """
        Initialize the middleware with the application and the container.

        Args:
            app: The FastAPI application.
            container_instance: The authoritative DI container instance.
        """
        super().__init__(app)
        self.container = container_instance
        logger.info("DIMiddleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        Attach the container to the request state and process the request.
        """
        request.state.container = self.container
        response = await call_next(request)
        return response


def inject_container(app: FastAPI, container_instance: DIContainer) -> None:
    """
    Configures the application to use the specified DI container.

    This function:
    1. Configures the container by registering all services.
    2. Adds the DIMiddleware to the application stack.

    Args:
        app: The FastAPI application.
        container_instance: The authoritative DI container for the application.
    """
    # Configure the container with all service definitions
    configure_container(container_instance)

    # Add the middleware to make the container available in requests
    app.add_middleware(DIMiddleware, container_instance=container_instance)

    logger.info("DI container injected into FastAPI application")


# The `with_injection` decorator has been removed as it was a relic of the
# previous global container system and is no longer used.
# FastAPI's `Depends` mechanism is the standard way to handle dependency
# injection in this architecture.
