"""
Core Package Initialization for Resync

This module initializes and exposes the core components of the Resync application.
"""

from .agent_manager import agent_manager
from .connection_manager import connection_manager
from .config_watcher import handle_config_change
from .knowledge_graph import knowledge_graph
from .metrics import metrics_registry

__all__ = [
    "agent_manager",
    "connection_manager",
    "handle_config_change",
    "knowledge_graph",
    "metrics_registry",
]
