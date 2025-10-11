"""
Centralized Dependency Injection (DI) Container for the Resync application.

This module initializes the DI container and registers all services and their
implementations, following the Inversion of Control (IoC) principle.
"""

from resync.core.agent_manager import AgentManager
from resync.core.connection_manager import ConnectionManager
from resync.core.di_container import (
    DIContainer,
    ServiceLifetime,
    register_default_services,
)
from resync.core.interfaces import (
    IAgentManager,
    IConnectionManager,
    IKnowledgeGraph,
    ITWSClient,
)
from resync.core.knowledge_graph import AsyncKnowledgeGraph
from resync.services.tws_service import OptimizedTWSClient
from resync.services.mock_tws_service import MockTWSClient
from resync.settings import settings


def create_container() -> DIContainer:
    """
    Creates and configures the DI container with all application services.
    """
    container = DIContainer()

    # Register default services
    register_default_services()

    # Register services with a SINGLETON scope to ensure a single instance
    # is shared across the application.
    container.register(IAgentManager, AgentManager, ServiceLifetime.SINGLETON)
    container.register(IConnectionManager, ConnectionManager, ServiceLifetime.SINGLETON)
    container.register(IKnowledgeGraph, AsyncKnowledgeGraph, ServiceLifetime.SINGLETON)

    # Register TWS client based on settings
    if settings.tws_mock_mode:
        container.register(ITWSClient, MockTWSClient, ServiceLifetime.SINGLETON)
    else:
        # Register factory function for OptimizedTWSClient with proper configuration
        def create_tws_client(container_instance):
            return OptimizedTWSClient(
                hostname=settings.tws_host or "localhost",
                port=settings.tws_port or 31111,
                username=settings.tws_user or "tws_user",
                password=settings.tws_password or "tws_password",
            )

        container.register_factory(
            ITWSClient, create_tws_client, ServiceLifetime.SINGLETON
        )

    return container


# Global container instance to be used by the application
app_container = create_container()
