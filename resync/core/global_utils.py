from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import CoreBootManager

# Global reference to boot manager
_boot_manager: Optional["CoreBootManager"] = None


def set_boot_manager(boot_manager: "CoreBootManager") -> None:
    """Set the global boot manager reference."""
    global _boot_manager
    _boot_manager = boot_manager


def get_global_correlation_id() -> str:
    """Get the global correlation ID for distributed tracing."""
    if _boot_manager is None:
        # Fallback if boot manager not set yet
        import time
        import os

        return f"fallback_{int(time.time())}_{os.urandom(4).hex()}"
    return _boot_manager.get_global_correlation_id()


def get_environment_tags() -> Dict[str, Any]:
    """Get environment tags for mock detection and debugging."""
    if _boot_manager is None:
        # Fallback if boot manager not set yet
        return {"boot_manager": "not_initialized"}
    return _boot_manager.get_environment_tags()
