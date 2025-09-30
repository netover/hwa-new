"""
Core package for the Resync application.

This __init__.py is kept minimal to avoid import-time side effects.
Services and components should be explicitly imported from their respective
modules.
"""

# This file is intentionally left mostly empty.
# The previous implementation contained complex, import-time initialization
# logic (CoreBootManager, global component registration) which violated
# best practices and caused startup failures (e.g., asyncio.run() in a
# running loop).

# The new architecture relies on an explicit dependency injection (DI)
# container configured at the application entry point (`resync.main.py`).
# All services should be registered and resolved through this container.

__all__ = []