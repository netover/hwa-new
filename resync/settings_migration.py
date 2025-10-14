"""Configuration migration helpers for settings updates.

This module provides utilities for migrating between different versions
of configuration settings, handling breaking changes and deprecations
gracefully.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

# Avoid circular import - Settings will be imported when needed
from .settings_factory import SettingsFactory
from .settings_observer import settings_monitor, ConfigurationChange, ChangeType


# Lazy import to avoid circular import
def _get_settings_class():
    from .settings import Settings

    return Settings


class MigrationType(Enum):
    """Types of configuration migrations."""

    FIELD_RENAMED = "field_renamed"
    FIELD_REMOVED = "field_removed"
    FIELD_ADDED = "field_added"
    VALUE_CHANGED = "value_changed"
    TYPE_CHANGED = "type_changed"
    VALIDATION_UPDATED = "validation_updated"
    DEFAULT_CHANGED = "default_changed"


@dataclass
class MigrationStep:
    """Represents a single migration step."""

    migration_type: MigrationType
    field_name: str
    old_name: Optional[str] = None
    new_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    value_mapping: Optional[Dict[Any, Any]] = None
    type_converter: Optional[str] = None
    description: str = ""
    breaking: bool = False
    version_introduced: str = ""

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this migration step to a configuration."""
        if self.migration_type == MigrationType.FIELD_RENAMED:
            return self._apply_field_rename(config)
        elif self.migration_type == MigrationType.FIELD_REMOVED:
            return self._apply_field_removal(config)
        elif self.migration_type == MigrationType.FIELD_ADDED:
            return self._apply_field_addition(config)
        elif self.migration_type == MigrationType.VALUE_CHANGED:
            return self._apply_value_change(config)
        elif self.migration_type == MigrationType.TYPE_CHANGED:
            return self._apply_type_change(config)
        elif self.migration_type == MigrationType.DEFAULT_CHANGED:
            return self._apply_default_change(config)

        return config

    def _apply_field_rename(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field rename migration."""
        if self.old_name and self.old_name in config:
            config[self.new_name or self.field_name] = config.pop(self.old_name)
        return config

    def _apply_field_removal(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field removal migration."""
        if self.field_name in config:
            del config[self.field_name]
        return config

    def _apply_field_addition(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field addition migration."""
        if self.field_name not in config:
            config[self.field_name] = self.new_value
        return config

    def _apply_value_change(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply value change migration."""
        if self.field_name in config and config[self.field_name] == self.old_value:
            if self.value_mapping:
                config[self.field_name] = self.value_mapping.get(
                    config[self.field_name], self.new_value
                )
            else:
                config[self.field_name] = self.new_value
        return config

    def _apply_type_change(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply type change migration."""
        if self.field_name in config and self.type_converter:
            try:
                if self.type_converter == "int":
                    config[self.field_name] = int(config[self.field_name])
                elif self.type_converter == "float":
                    config[self.field_name] = float(config[self.field_name])
                elif self.type_converter == "bool":
                    config[self.field_name] = str(config[self.field_name]).lower() in (
                        "true",
                        "1",
                        "yes",
                    )
                elif self.type_converter == "str":
                    config[self.field_name] = str(config[self.field_name])
            except (ValueError, TypeError):
                # If conversion fails, use new default value
                config[self.field_name] = self.new_value
        return config

    def _apply_default_change(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default value change migration."""
        if self.field_name not in config:
            config[self.field_name] = self.new_value
        return config


@dataclass
class Migration:
    """Represents a complete migration with multiple steps."""

    version: str
    description: str
    steps: List[MigrationStep] = field(default_factory=list)
    breaking: bool = False
    rollback_steps: List[MigrationStep] = field(default_factory=list)

    def apply(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all migration steps to configuration."""
        migrated_config = config.copy()

        for step in self.steps:
            migrated_config = step.apply(migrated_config)

        return migrated_config

    def rollback(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback migration steps."""
        rolled_back_config = config.copy()

        for step in reversed(self.rollback_steps):
            rolled_back_config = step.apply(rolled_back_config)

        return rolled_back_config


class MigrationManager:
    """Manages configuration migrations."""

    def __init__(self):
        self.migrations: Dict[str, Migration] = {}
        self.migration_history: List[Dict[str, Any]] = []
        self.history_file: Optional[Path] = None

    def register_migration(self, migration: Migration) -> None:
        """Register a migration."""
        self.migrations[migration.version] = migration

    def get_migrations_to_apply(
        self, current_version: str, target_version: Optional[str] = None
    ) -> List[Migration]:
        """Get list of migrations to apply from current to target version."""
        if target_version is None:
            target_version = self.get_latest_version()

        migrations_to_apply = []

        # Simple version comparison (assuming semantic versioning)
        current_parts = [int(x) for x in current_version.split(".")]
        target_parts = [int(x) for x in target_version.split(".")]

        for version, migration in sorted(self.migrations.items()):
            version_parts = [int(x) for x in version.split(".")]

            if version_parts > current_parts and version_parts <= target_parts:
                migrations_to_apply.append(migration)

        return migrations_to_apply

    def get_latest_version(self) -> str:
        """Get the latest migration version."""
        if not self.migrations:
            return "1.0.0"

        return max(self.migrations.keys())

    def migrate_config(
        self,
        config: Dict[str, Any],
        from_version: str,
        to_version: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Migrate configuration from one version to another."""
        migrations_to_apply = self.get_migrations_to_apply(from_version, to_version)
        migrated_config = config.copy()
        applied_migrations = []

        for migration in migrations_to_apply:
            old_config = migrated_config.copy()
            migrated_config = migration.apply(migrated_config)

            # Record migration
            migration_record = {
                "timestamp": time.time(),
                "from_version": from_version,
                "to_version": migration.version,
                "migration_version": migration.version,
                "description": migration.description,
                "breaking": migration.breaking,
                "config_changes": self._get_config_changes(old_config, migrated_config),
            }

            self.migration_history.append(migration_record)
            applied_migrations.append(migration.version)

            # Update current version
            from_version = migration.version

        return migrated_config, applied_migrations

    def _get_config_changes(
        self, old_config: Dict[str, Any], new_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get list of changes between old and new config."""
        changes = []

        all_keys = set(old_config.keys()) | set(new_config.keys())

        for key in all_keys:
            old_value = old_config.get(key)
            new_value = new_config.get(key)

            if old_value != new_value:
                changes.append(
                    {
                        "field": key,
                        "old_value": old_value,
                        "new_value": new_value,
                        "change_type": (
                            "modified"
                            if key in old_config and key in new_config
                            else "added" if key in new_config else "removed"
                        ),
                    }
                )

        return changes

    def save_migration_history(self, file_path: Optional[Path] = None) -> None:
        """Save migration history to file."""
        if file_path is None:
            file_path = self.history_file or Path("migration_history.json")

        history_data = {
            "last_updated": datetime.now().isoformat(),
            "migrations": self.migration_history,
        }

        with open(file_path, "w") as f:
            json.dump(history_data, f, indent=2, default=str)

    def load_migration_history(self, file_path: Optional[Path] = None) -> None:
        """Load migration history from file."""
        if file_path is None:
            file_path = self.history_file or Path("migration_history.json")

        if not file_path.exists():
            return

        try:
            with open(file_path, "r") as f:
                history_data = json.load(f)

            self.migration_history = history_data.get("migrations", [])
        except Exception:
            # If file is corrupted, start fresh
            self.migration_history = []


class SettingsMigrationHelper:
    """Helper class for settings-specific migrations."""

    def __init__(self):
        self.migration_manager = MigrationManager()
        self._setup_default_migrations()

    def _setup_default_migrations(self) -> None:
        """Setup default migrations for common configuration changes."""

        # Migration 1.1.0: Cache configuration improvements
        migration_1_1_0 = Migration(
            version="1.1.0",
            description="Cache configuration improvements",
            steps=[
                MigrationStep(
                    migration_type=MigrationType.FIELD_ADDED,
                    field_name="cache_hierarchy_l2_cleanup_interval",
                    new_value=60,
                    description="Add cache cleanup interval configuration",
                ),
                MigrationStep(
                    migration_type=MigrationType.DEFAULT_CHANGED,
                    field_name="cache_hierarchy_l1_max_size",
                    new_value=5000,
                    description="Update default L1 cache size",
                ),
            ],
        )

        # Migration 1.2.0: Security enhancements
        migration_1_2_0 = Migration(
            version="1.2.0",
            description="Security enhancements",
            steps=[
                MigrationStep(
                    migration_type=MigrationType.FIELD_ADDED,
                    field_name="cors_allow_credentials",
                    new_value=True,
                    description="Add CORS credentials configuration",
                ),
                MigrationStep(
                    migration_type=MigrationType.VALUE_CHANGED,
                    field_name="admin_password",
                    old_value="change_me_please",
                    new_value=None,
                    description="Remove insecure default password",
                ),
            ],
        )

        # Migration 1.3.0: Connection pool improvements
        migration_1_3_0 = Migration(
            version="1.3.0",
            description="Connection pool improvements",
            steps=[
                MigrationStep(
                    migration_type=MigrationType.FIELD_ADDED,
                    field_name="db_pool_health_check_interval",
                    new_value=60,
                    description="Add database pool health check interval",
                ),
                MigrationStep(
                    migration_type=MigrationType.FIELD_ADDED,
                    field_name="redis_pool_health_check_interval",
                    new_value=60,
                    description="Add Redis pool health check interval",
                ),
            ],
        )

        # Register migrations
        self.migration_manager.register_migration(migration_1_1_0)
        self.migration_manager.register_migration(migration_1_2_0)
        self.migration_manager.register_migration(migration_1_3_0)

    def migrate_settings(
        self, settings: Any, target_version: Optional[str] = None
    ) -> Tuple[Any, List[str]]:
        """Migrate settings to target version."""
        # Convert settings to dict
        config_dict = settings.__dict__.copy()

        # Add current version if not present
        current_version = getattr(settings, "_version", "1.0.0")

        # Migrate configuration
        migrated_config, applied_migrations = self.migration_manager.migrate_config(
            config_dict, current_version, target_version
        )

        # Create new settings with migrated config
        try:
            Settings = _get_settings_class()
            migrated_settings = Settings(**migrated_config)
            # Set version attribute
            migrated_settings._version = (
                target_version or self.migration_manager.get_latest_version()
            )

            # Notify observers of migration
            if applied_migrations:
                change = ConfigurationChange(
                    change_type=ChangeType.UPDATED,
                    setting_key="settings_migration",
                    old_value=current_version,
                    new_value=migrated_settings._version,
                    timestamp=time.time(),
                    environment=settings.environment.value,
                    metadata={
                        "applied_migrations": applied_migrations,
                        "migration_type": "settings_upgrade",
                    },
                )
                settings_monitor.subject.notify_observers(change)

            return migrated_settings, applied_migrations

        except Exception as e:
            # If migration fails, return original settings
            print(f"Migration failed: {e}")
            return settings, []

    def create_backup_settings(
        self, settings: Any, backup_path: Optional[Path] = None
    ) -> Path:
        """Create backup of current settings before migration."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(f"settings_backup_{timestamp}.json")

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "version": getattr(settings, "_version", "1.0.0"),
            "environment": settings.environment.value,
            "settings": settings.__dict__,
        }

        with open(backup_path, "w") as f:
            json.dump(backup_data, f, indent=2, default=str)

        return backup_path

    def get_migration_preview(
        self, settings: Any, target_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get preview of what would change in migration."""
        config_dict = settings.__dict__.copy()
        current_version = getattr(settings, "_version", "1.0.0")

        migrations_to_apply = self.migration_manager.get_migrations_to_apply(
            current_version, target_version
        )

        preview_config = config_dict.copy()
        changes_summary = []

        for migration in migrations_to_apply:
            old_config = preview_config.copy()
            preview_config = migration.apply(preview_config)

            # Get changes for this migration
            migration_changes = self.migration_manager._get_config_changes(
                old_config, preview_config
            )

            changes_summary.append(
                {
                    "migration_version": migration.version,
                    "description": migration.description,
                    "breaking": migration.breaking,
                    "changes": migration_changes,
                }
            )

        return {
            "current_version": current_version,
            "target_version": target_version
            or self.migration_manager.get_latest_version(),
            "migrations_to_apply": [m.version for m in migrations_to_apply],
            "changes_summary": changes_summary,
            "preview_config": preview_config,
        }


# Global migration helper instance
settings_migration_helper = SettingsMigrationHelper()
