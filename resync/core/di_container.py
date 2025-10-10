from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime
from enum import Enum, auto
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Protocol,
    Type,
    TypeVar,
    cast,
    get_type_hints,
)

# --- Logging Setup ---
from resync.core.structured_logger import get_logger

logger = get_logger(__name__)

# --- Type Variables ---
T = TypeVar("T")
TInterface = TypeVar("TInterface")
TImplementation = TypeVar("TImplementation")


class ServiceLifetime(Enum):
    """Defines the lifecycle scope of a registered service."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class DIContainer:
    """Thread-safe DI container with proper lifecycle management."""
    
    def __init__(self):
        self._factories: Dict[type, tuple[Callable, ServiceLifetime]] = {}
        self._singletons: Dict[type, Any] = {}
        self._locks: Dict[type, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
    
    def register(
        self,
        interface: type[T],
        factory: Callable[[], T],
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    ):
        """Register service factory."""
        self._factories[interface] = (factory, lifetime)
        if lifetime == ServiceLifetime.SINGLETON:
            self._locks[interface] = asyncio.Lock()
    
    def register_instance(self, interface: type[T], instance: T):
        """Register pre-created instance."""
        self._singletons[interface] = instance
        self._factories[interface] = (lambda: instance, ServiceLifetime.SINGLETON)
    
    async def get(self, interface: type[T]) -> T:
        """
        Resolve service with double-checked locking pattern.
        """
        if interface not in self._factories:
            raise ValueError(f"Service {interface.__name__} not registered")
        
        factory, lifetime = self._factories[interface]
        
        if lifetime == ServiceLifetime.SINGLETON:
            # Double-checked locking for singletons
            if interface in self._singletons:
                return self._singletons[interface]
            
            async with self._locks[interface]:
                # Check again after acquiring lock
                if interface in self._singletons:
                    return self._singletons[interface]
                
                instance = await self._create_instance(factory)
                self._singletons[interface] = instance
                return instance
        
        elif lifetime == ServiceLifetime.TRANSIENT:
            # Always create new instance
            return await self._create_instance(factory)
        
        else:  # SCOPED
            # Get from current scope (request context)
            scope = await self._get_current_scope()
            if interface not in scope:
                scope[interface] = await self._create_instance(factory)
            return scope[interface]
    
    async def _create_instance(self, factory: Callable) -> Any:
        """Create instance handling async factories."""
        if asyncio.iscoroutinefunction(factory):
            return await factory()
        return factory()
    
    async def _get_current_scope(self) -> Dict[type, Any]:
        """Get or create scope for current request/context."""
        # Use context vars for scope isolation
        # Implementation depends on your framework
        # For now, return a new dict for each call
        return {}


# --- Global Container Instance ---
# This is the default container used by the application.
# It can be replaced with a custom container if needed.
container = DIContainer()


def register_default_services():
    """Register default services with the container."""
    from resync.core.audit_queue import AsyncAuditQueue, IAuditQueue
    container.register(IAuditQueue, AsyncAuditQueue, lifetime=ServiceLifetime.SINGLETON)


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    return container