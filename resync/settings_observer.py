"""Observer pattern implementation for settings configuration changes.

This module provides the observer pattern infrastructure to notify components
when settings configuration changes occur, enabling reactive responses to
configuration updates.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TypeVar
from weakref import WeakSet

# Avoid circular import - Settings will be imported when needed


# Lazy import to avoid circular import
def _get_settings_class():
    from .settings import Settings

    return Settings


class ChangeType(Enum):
    """Types of configuration changes."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    ENVIRONMENT_CHANGED = "environment_changed"
    SECURITY_UPDATED = "security_updated"
    PERFORMANCE_UPDATED = "performance_updated"


@dataclass
class ConfigurationChange:
    """Represents a configuration change event."""

    change_type: ChangeType
    setting_key: str
    old_value: Any
    new_value: Any
    timestamp: float
    environment: str
    metadata: Optional[Dict[str, Any]] = None


class SettingsObserver(ABC):
    """Abstract base class for settings observers."""

    @abstractmethod
    def on_settings_change(self, change: ConfigurationChange) -> None:
        """Called when settings configuration changes.

        Args:
            change: Details of the configuration change
        """
        pass

    @abstractmethod
    def get_observer_id(self) -> str:
        """Get unique identifier for this observer."""
        pass

    def get_interested_keys(self) -> Optional[Set[str]]:
        """Get set of setting keys this observer is interested in.

        Returns:
            Set of keys or None for all keys
        """
        return None

    def get_interested_change_types(self) -> Optional[Set[ChangeType]]:
        """Get set of change types this observer is interested in.

        Returns:
            Set of change types or None for all types
        """
        return None


T = TypeVar("T", bound=SettingsObserver)


class SettingsSubject:
    """Subject class that manages observers and notifies them of changes."""

    def __init__(self):
        self._observers: WeakSet[SettingsObserver] = WeakSet()
        self._lock = threading.RLock()
        self._change_history: List[ConfigurationChange] = []
        self._max_history_size = 1000

    def attach(self, observer: SettingsObserver) -> None:
        """Attach an observer to receive notifications."""
        with self._lock:
            self._observers.add(observer)

    def detach(self, observer: SettingsObserver) -> None:
        """Detach an observer from receiving notifications."""
        with self._lock:
            self._observers.discard(observer)

    def notify_observers(self, change: ConfigurationChange) -> None:
        """Notify all observers of a configuration change."""
        with self._lock:
            # Add to history
            self._change_history.append(change)
            if len(self._change_history) > self._max_history_size:
                self._change_history.pop(0)

            # Notify observers
            for observer in list(self._observers):
                try:
                    # Check if observer is interested in this change
                    if self._should_notify_observer(observer, change):
                        observer.on_settings_change(change)
                except ReferenceError:
                    # Observer was garbage collected
                    self._observers.discard(observer)
                except Exception as e:
                    # Log error but continue with other observers
                    print(f"Error notifying observer {observer.get_observer_id()}: {e}")

    def _should_notify_observer(
        self, observer: SettingsObserver, change: ConfigurationChange
    ) -> bool:
        """Check if observer should be notified of this change."""
        # Check interested keys
        interested_keys = observer.get_interested_keys()
        if interested_keys is not None and change.setting_key not in interested_keys:
            return False

        # Check interested change types
        interested_types = observer.get_interested_change_types()
        if interested_types is not None and change.change_type not in interested_types:
            return False

        return True

    def get_change_history(
        self,
        limit: Optional[int] = None,
        key_filter: Optional[str] = None,
        type_filter: Optional[ChangeType] = None,
    ) -> List[ConfigurationChange]:
        """Get change history with optional filtering."""
        with self._lock:
            history = self._change_history

            if key_filter:
                history = [c for c in history if c.setting_key == key_filter]

            if type_filter:
                history = [c for c in history if c.change_type == type_filter]

            if limit:
                history = history[-limit:]

            return history.copy()

    def clear_history(self) -> None:
        """Clear the change history."""
        with self._lock:
            self._change_history.clear()


class LoggingObserver(SettingsObserver):
    """Observer that logs configuration changes."""

    def __init__(self, name: str = "SettingsLogger"):
        self.name = name

    def on_settings_change(self, change: ConfigurationChange) -> None:
        """Log the configuration change."""
        print(
            f"[{self.name}] {change.change_type.value}: "
            f"{change.setting_key} = {change.old_value} -> {change.new_value} "
            f"({change.environment})"
        )

    def get_observer_id(self) -> str:
        return self.name


class CacheInvalidationObserver(SettingsObserver):
    """Observer that handles cache invalidation on configuration changes."""

    def __init__(self, cache_manager: Any = None):
        self.cache_manager = cache_manager
        self.name = "CacheInvalidationObserver"

    def on_settings_change(self, change: ConfigurationChange) -> None:
        """Invalidate relevant caches based on configuration change."""
        cache_keys_to_invalidate = self._get_cache_keys_for_change(change)

        if cache_keys_to_invalidate and self.cache_manager:
            for key in cache_keys_to_invalidate:
                try:
                    self.cache_manager.invalidate(key)
                except Exception as e:
                    print(f"Error invalidating cache key {key}: {e}")

    def _get_cache_keys_for_change(self, change: ConfigurationChange) -> List[str]:
        """Get cache keys that should be invalidated for a given change."""
        keys_to_invalidate = []

        # Map setting keys to cache keys
        cache_key_mapping = {
            "redis_url": ["redis:connection", "redis:pool"],
            "neo4j_uri": ["neo4j:connection", "neo4j:pool"],
            "llm_endpoint": ["llm:client", "llm:cache"],
            "cors_allowed_origins": ["cors:config"],
            "rate_limit_*": ["rate_limit:config"],
        }

        for pattern, cache_keys in cache_key_mapping.items():
            if pattern.endswith("*"):
                if change.setting_key.startswith(pattern[:-1]):
                    keys_to_invalidate.extend(cache_keys)
            elif change.setting_key == pattern:
                keys_to_invalidate.extend(cache_keys)

        return keys_to_invalidate

    def get_observer_id(self) -> str:
        return self.name

    def get_interested_keys(self) -> Optional[Set[str]]:
        """Only interested in connection and configuration related keys."""
        return {
            "redis_url",
            "neo4j_uri",
            "llm_endpoint",
            "cors_allowed_origins",
            "rate_limit_public_per_minute",
            "rate_limit_authenticated_per_minute",
        }


class MetricsObserver(SettingsObserver):
    """Observer that tracks configuration change metrics."""

    def __init__(self, metrics_client: Any = None):
        self.metrics_client = metrics_client
        self.name = "MetricsObserver"
        self._change_counts = {}
        self._lock = threading.Lock()

    def on_settings_change(self, change: ConfigurationChange) -> None:
        """Record metrics for configuration change."""
        with self._lock:
            key = f"{change.environment}:{change.setting_key}"
            self._change_counts[key] = self._change_counts.get(key, 0) + 1

        # Record metrics if client available
        if self.metrics_client:
            try:
                self.metrics_client.increment_counter(
                    "settings_changes_total",
                    tags={
                        "environment": change.environment,
                        "setting_key": change.setting_key,
                        "change_type": change.change_type.value,
                    },
                )
            except Exception as e:
                print(f"Error recording metrics: {e}")

    def get_observer_id(self) -> str:
        return self.name

    def get_change_counts(self) -> Dict[str, int]:
        """Get current change counts."""
        with self._lock:
            return self._change_counts.copy()


class SettingsMonitor:
    """Monitor class that tracks settings changes and manages observers."""

    def __init__(self):
        self.subject = SettingsSubject()
        self._current_settings: Optional[Any] = None
        self._lock = threading.Lock()

    def set_settings(self, settings: Any) -> None:
        """Set new settings and notify observers of changes."""
        with self._lock:
            old_settings = self._current_settings
            self._current_settings = settings

            if old_settings is not None:
                self._notify_changes(old_settings, settings)
            else:
                # First time setting - notify creation
                self._notify_creation(settings)

    def get_settings(self) -> Optional[Any]:
        """Get current settings."""
        with self._lock:
            return self._current_settings

    def _notify_creation(self, settings: Any) -> None:
        """Notify observers of settings creation."""
        change = ConfigurationChange(
            change_type=ChangeType.CREATED,
            setting_key="settings",
            old_value=None,
            new_value=settings.__dict__,
            timestamp=time.time(),
            environment=settings.environment.value,
        )
        self.subject.notify_observers(change)

    def _notify_changes(self, old_settings: Any, new_settings: Any) -> None:
        """Notify observers of specific setting changes."""
        # Check environment change first
        if old_settings.environment != new_settings.environment:
            change = ConfigurationChange(
                change_type=ChangeType.ENVIRONMENT_CHANGED,
                setting_key="environment",
                old_value=old_settings.environment.value,
                new_value=new_settings.environment.value,
                timestamp=time.time(),
                environment=new_settings.environment.value,
            )
            self.subject.notify_observers(change)

        # Check individual field changes
        all_fields = set(old_settings.__dict__.keys()) | set(
            new_settings.__dict__.keys()
        )

        for field in all_fields:
            old_value = getattr(old_settings, field, None)
            new_value = getattr(new_settings, field, None)

            if old_value != new_value:
                # Determine change type based on field
                change_type = self._determine_change_type(field, old_value, new_value)

                change = ConfigurationChange(
                    change_type=change_type,
                    setting_key=field,
                    old_value=old_value,
                    new_value=new_value,
                    timestamp=time.time(),
                    environment=new_settings.environment.value,
                    metadata={"field_type": type(new_value).__name__},
                )
                self.subject.notify_observers(change)

    def _determine_change_type(
        self, field: str, old_value: Any, new_value: Any
    ) -> ChangeType:
        """Determine the type of change for a field."""
        if old_value is None and new_value is not None:
            return ChangeType.CREATED
        elif old_value is not None and new_value is None:
            return ChangeType.DELETED
        else:
            # Check if it's a security-related field
            security_fields = {
                "admin_password",
                "llm_api_key",
                "tws_password",
                "cors_allowed_origins",
                "cors_allow_credentials",
            }
            if field in security_fields:
                return ChangeType.SECURITY_UPDATED

            # Check if it's a performance-related field
            performance_fields = {
                "db_pool_min_size",
                "db_pool_max_size",
                "redis_pool_min_size",
                "redis_pool_max_size",
                "http_pool_min_size",
                "http_pool_max_size",
                "cache_hierarchy_l1_max_size",
                "cache_hierarchy_l2_ttl",
            }
            if field in performance_fields:
                return ChangeType.PERFORMANCE_UPDATED

            return ChangeType.UPDATED

    def attach_observer(self, observer: SettingsObserver) -> None:
        """Attach an observer."""
        self.subject.attach(observer)

    def detach_observer(self, observer: SettingsObserver) -> None:
        """Detach an observer."""
        self.subject.detach(observer)

    def get_change_history(self, **kwargs) -> List[ConfigurationChange]:
        """Get change history."""
        return self.subject.get_change_history(**kwargs)

    def clear_history(self) -> None:
        """Clear change history."""
        self.subject.clear_history()


# Global settings monitor instance
settings_monitor = SettingsMonitor()
