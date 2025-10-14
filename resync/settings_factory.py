"""Factory for creating environment-specific settings configurations.

This module provides factory classes for creating settings optimized for
different deployment environments (development, production, test).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field

from .settings_validator import Environment
from .settings_validator import SettingsValidator


# Lazy import to avoid circular import
def _get_settings_class():
    from .settings import Settings

    return Settings


class EnvironmentConfig(ABC):
    """Abstract base class for environment-specific configurations."""

    @abstractmethod
    def get_default_overrides(self) -> Dict[str, Any]:
        """Get default configuration overrides for this environment."""
        pass

    @abstractmethod
    def get_security_overrides(self) -> Dict[str, Any]:
        """Get security-related overrides for this environment."""
        pass

    @abstractmethod
    def get_performance_overrides(self) -> Dict[str, Any]:
        """Get performance-related overrides for this environment."""
        pass


class DevelopmentConfig(EnvironmentConfig):
    """Configuration for development environment."""

    def get_default_overrides(self) -> Dict[str, Any]:
        """Development-optimized defaults."""
        return {
            "environment": Environment.DEVELOPMENT,
            "log_level": "DEBUG",
            "tws_mock_mode": True,
            "cors_allowed_origins": ["*"],
            "cors_allow_credentials": True,
            "admin_password": "dev_password_123",
            "llm_api_key": "dummy_key_for_development",
            "redis_url": "redis://localhost:6379/0",
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_password": "dev_password",
        }

    def get_security_overrides(self) -> Dict[str, Any]:
        """Relaxed security for development."""
        return {
            "cors_allow_methods": ["*"],
            "cors_allow_headers": ["*"],
            "static_cache_max_age": 0,  # Disable cache for development
        }

    def get_performance_overrides(self) -> Dict[str, Any]:
        """Development performance settings."""
        return {
            "db_pool_min_size": 5,
            "db_pool_max_size": 20,
            "redis_pool_min_size": 2,
            "redis_pool_max_size": 10,
            "http_pool_min_size": 5,
            "http_pool_max_size": 20,
        }


class ProductionConfig(EnvironmentConfig):
    """Configuration for production environment."""

    def get_default_overrides(self) -> Dict[str, Any]:
        """Production-ready defaults."""
        return {
            "environment": Environment.PRODUCTION,
            "log_level": "INFO",
            "tws_mock_mode": False,  # Require real TWS connection
            "cors_allowed_origins": [],  # Must be explicitly set
            "cors_allow_credentials": False,
            "static_cache_max_age": 3600,
        }

    def get_security_overrides(self) -> Dict[str, Any]:
        """Enhanced security for production."""
        return {
            "cors_allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "cors_allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "admin_password": None,  # Must be set via environment
            "llm_api_key": None,  # Must be set via environment
        }

    def get_performance_overrides(self) -> Dict[str, Any]:
        """Production performance settings."""
        return {
            "db_pool_min_size": 20,
            "db_pool_max_size": 100,
            "redis_pool_min_size": 10,
            "redis_pool_max_size": 50,
            "http_pool_min_size": 20,
            "http_pool_max_size": 100,
            "cache_hierarchy_l1_max_size": 10000,
            "cache_hierarchy_l2_ttl": 1800,
        }


class TestConfig(EnvironmentConfig):
    """Configuration for testing environment."""

    def get_default_overrides(self) -> Dict[str, Any]:
        """Test-optimized defaults."""
        return {
            "environment": Environment.TEST,
            "log_level": "WARNING",
            "tws_mock_mode": True,
            "cors_allowed_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "cors_allow_credentials": True,
            "admin_password": "test_password_123",
            "llm_api_key": "test_key_123",
            "redis_url": "redis://localhost:6379/15",  # Use different DB for tests
            "neo4j_uri": "bolt://localhost:7688",  # Use different port for tests
            "neo4j_password": "test_password",
        }

    def get_security_overrides(self) -> Dict[str, Any]:
        """Test security settings."""
        return {
            "cors_allow_methods": ["*"],
            "cors_allow_headers": ["*"],
            "static_cache_max_age": 0,
        }

    def get_performance_overrides(self) -> Dict[str, Any]:
        """Test performance settings."""
        return {
            "db_pool_min_size": 1,
            "db_pool_max_size": 5,
            "redis_pool_min_size": 1,
            "redis_pool_max_size": 5,
            "http_pool_min_size": 1,
            "http_pool_max_size": 5,
            "cache_hierarchy_l1_max_size": 100,
            "cache_hierarchy_l2_ttl": 60,
        }


class SettingsFactory:
    """Factory for creating environment-specific settings."""

    _env_configs = {
        Environment.DEVELOPMENT: DevelopmentConfig(),
        Environment.PRODUCTION: ProductionConfig(),
        Environment.TEST: TestConfig(),
    }

    @classmethod
    def create_for_environment(
        cls,
        environment: Environment,
        overrides: Optional[Dict[str, Any]] = None,
        config_type: str = "default",
    ):
        """Create settings for a specific environment.

        Args:
            environment: Target environment
            overrides: Optional configuration overrides
            config_type: Type of configuration ("default", "security", "performance")

        Returns:
            Configured Settings instance
        """
        if environment not in cls._env_configs:
            raise ValueError(f"Unsupported environment: {environment}")

        env_config = cls._env_configs[environment]

        # Get base overrides based on config type
        if config_type == "security":
            base_overrides = env_config.get_security_overrides()
        elif config_type == "performance":
            base_overrides = env_config.get_performance_overrides()
        else:
            base_overrides = env_config.get_default_overrides()

        # Apply user overrides
        if overrides:
            base_overrides.update(overrides)

        # Create settings with environment-specific defaults
        Settings = _get_settings_class()
        return Settings(**base_overrides)

    @classmethod
    def create_development(cls, overrides: Optional[Dict[str, Any]] = None):
        """Create development-optimized settings."""
        return cls.create_for_environment(Environment.DEVELOPMENT, overrides)

    @classmethod
    def create_production(cls, overrides: Optional[Dict[str, Any]] = None):
        """Create production-ready settings."""
        return cls.create_for_environment(Environment.PRODUCTION, overrides)

    @classmethod
    def create_test(cls, overrides: Optional[Dict[str, Any]] = None):
        """Create test-optimized settings."""
        return cls.create_for_environment(Environment.TEST, overrides)

    @classmethod
    def create_from_env_file(
        cls, env_file: str = ".env", overrides: Optional[Dict[str, Any]] = None
    ):
        """Create settings from environment file with optional overrides."""
        # Read environment file and merge with overrides
        env_overrides = cls._read_env_file(env_file)
        if overrides:
            env_overrides.update(overrides)

        # Determine environment from file or use default
        environment = env_overrides.get("environment", Environment.DEVELOPMENT)

        return cls.create_for_environment(environment, env_overrides)

    @classmethod
    def _read_env_file(cls, env_file: str) -> Dict[str, Any]:
        """Read environment file and return configuration dict."""
        env_overrides = {}
        env_path = Path(env_file)

        if not env_path.exists():
            return env_overrides

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Convert to appropriate types
                        if value.lower() in ("true", "false"):
                            env_overrides[key.lower()] = value.lower() == "true"
                        elif value.isdigit():
                            env_overrides[key.lower()] = int(value)
                        elif value.replace(".", "", 1).isdigit():
                            env_overrides[key.lower()] = float(value)
                        else:
                            env_overrides[key.lower()] = value
        except Exception:
            # If file can't be read, return empty dict
            pass

        return env_overrides

    @classmethod
    def get_available_config_types(cls) -> list[str]:
        """Get list of available configuration types."""
        return ["default", "security", "performance"]

    @classmethod
    def get_supported_environments(cls) -> list[Environment]:
        """Get list of supported environments."""
        return list(cls._env_configs.keys())
