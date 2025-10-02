"""
Centralized Dependency Injection (DI) Container for the Resync application.

This module initializes the DI container and registers all services and their
implementations, following the Inversion of Control (IoC) principle.
"""

from resync.core.di_container import DIContainer, ServiceScope
from resync.core.interfaces import (
    IAgentManager,
    IConnectionManager,
    IKnowledgeGraph,
)
from resync.core.agent_manager import AgentManager
from resync.core.connection_manager import ConnectionManager
from resync.core.knowledge_graph import AsyncKnowledgeGraph


def create_container() -> DIContainer:
    """
    Creates and configures the DI container with all application services.
    """
    container = DIContainer()

    # Register services with a SINGLETON scope to ensure a single instance
    # is shared across the application.
    container.register(IAgentManager, AgentManager, ServiceScope.SINGLETON)
    container.register(IConnectionManager, ConnectionManager, ServiceScope.SINGLETON)
    container.register(IKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON)

    return container


# Global container instance to be used by the application
app_container = create_container()