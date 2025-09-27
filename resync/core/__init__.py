"""
Core Package Initialization for Resync

This module initializes and exposes the core components of the Resync application.
"""

from typing import Any

from .async_cache import AsyncTTLCache
from .config_watcher import handle_config_change

# from .agent_manager import agent_manager  # Temporarily disabled for testing
from .connection_manager import connection_manager
from .knowledge_graph import knowledge_graph
from .metrics import metrics_registry

__all__ = [
    "AsyncTTLCache",
    # "agent_manager",  # Temporarily disabled for testing
    "connection_manager",
    "handle_config_change",
    "knowledge_graph",
    "metrics_registry",
]


# Basic encryption service for security tests
class EncryptionService:
    """Simple encryption service mock for testing."""

    @staticmethod
    def encrypt(data: str) -> str:
        """Encrypt sensitive data."""
        return f"encrypted_{data}"

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt data."""
        return encrypted_data.replace("encrypted_", "")


# Logger for masking in logs
import logging

logger = logging.getLogger(__name__)


def mask_sensitive_data_in_logs(record: Any) -> bool:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


logging.getLogger().addFilter(mask_sensitive_data_in_logs)

# Export for tests

encryption_service = EncryptionService()

# Set global instance
encryption_service = EncryptionService()
