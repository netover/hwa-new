"""Smart pytest configuration for optional dependencies.

This conftest.py only creates mocks for modules that actually fail to import,
preventing collection errors while allowing tests to run normally.
"""

import os
import sys
import types
# Desabilita integrações pesadas durante a coleta
os.environ.setdefault("RESYNC_DISABLE_REDIS", "1")
os.environ.setdefault("RESYNC_EAGER_BOOT", "0")

# Mocks mínimos para dependências opcionais
for name in ("redis", "redis.asyncio", "uvloop", "websockets"):
    if name not in sys.modules:
        sys.modules[name] = types.SimpleNamespace()

import importlib
from unittest.mock import MagicMock


def _smart_import_hook(name, *args, **kwargs):
    """Hook that creates mocks only when imports actually fail."""
    try:
        return importlib.__import__(name, *args, **kwargs)
    except ImportError:
        # Only create mock for known optional dependencies
        if name in ("aiofiles", "redis", "uvloop", "websockets"):
            mock = MagicMock()
            mock.__name__ = name
            mock.__module__ = name
            # Store in sys.modules to prevent repeated import attempts
            sys.modules[name] = mock
            return mock
        # Re-raise for other imports
        raise


# Monkey patch import temporarily during collection
_original_import = __builtins__['__import__']
__builtins__['__import__'] = _smart_import_hook