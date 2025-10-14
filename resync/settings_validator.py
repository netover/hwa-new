"""Configuration validators for settings module.

This module contains all validation logic extracted from the Settings class
to improve maintainability and separation of concerns.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import ValidationInfo


class Environment(str, Enum):
    """Ambientes suportados."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class SettingsValidator:
    """Centralized validation logic for settings configuration."""

    # Insecure passwords for production validation
    INSECURE_PASSWORDS = {
        "change_me_please",
        "change_me_immediately",
        "admin",
        "password",
        "12345678",
    }

    # Common TWS passwords to avoid
    COMMON_TWS_PASSWORDS = {"password", "twsuser", "tws_password", "change_me"}

    @staticmethod
    def validate_base_dir(v) -> Path:
        """Resolve base_dir to absolute path."""
        if isinstance(v, str):
            v = Path(v)
        return v.resolve()

    @staticmethod
    def validate_db_pool_sizes(
        max_size: int, min_size: int, field_name: str = "db_pool"
    ) -> int:
        """Validate that max_size >= min_size for database pools."""
        if max_size < min_size:
            raise ValueError(
                f"{field_name}_max_size ({max_size}) must be >= {field_name}_min_size ({min_size})"
            )
        return max_size

    @staticmethod
    def validate_redis_pool_sizes(
        max_size: int, min_size: int, field_name: str = "redis_pool"
    ) -> int:
        """Validate that max_size >= min_size for Redis pools."""
        if max_size < min_size:
            raise ValueError(
                f"{field_name}_max_size ({max_size}) must be >= {field_name}_min_size ({min_size})"
            )
        return max_size

    @staticmethod
    def validate_redis_url(redis_url: str) -> str:
        """Validate Redis URL format."""
        if not redis_url.startswith("redis://"):
            raise ValueError(
                "REDIS_URL must start with 'redis://'. "
                "Example: redis://localhost:6379 or redis://:password@localhost:6379"
            )
        return redis_url

    @staticmethod
    def validate_password_strength(password: str) -> str:
        """Validate minimum password strength."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return password

    @staticmethod
    def validate_production_password(
        password: str, environment: Environment, field_name: str = "admin_password"
    ) -> str:
        """Validate password security in production."""
        if environment == Environment.PRODUCTION:
            if password.lower() in SettingsValidator.INSECURE_PASSWORDS:
                raise ValueError(f"Insecure {field_name} not allowed in production")
        return password

    @staticmethod
    def validate_production_cors(
        cors_origins: list[str], environment: Environment
    ) -> list[str]:
        """Validate CORS configuration in production."""
        if environment == Environment.PRODUCTION and "*" in cors_origins:
            raise ValueError("Wildcard CORS origins not allowed in production")
        return cors_origins

    @staticmethod
    def validate_llm_api_key_production(api_key: str, environment: Environment) -> str:
        """Validate LLM API key in production."""
        if environment == Environment.PRODUCTION:
            if api_key == "dummy_key_for_development":
                raise ValueError("LLM_API_KEY must be set to a valid key in production")
        return api_key

    @staticmethod
    def validate_tws_credentials_production(
        credential: str | None, environment: Environment, field_name: str
    ) -> str | None:
        """Validate TWS credentials in production."""
        if credential and environment == Environment.PRODUCTION:
            if field_name == "tws_password":
                if len(credential) < 12:
                    raise ValueError(
                        "TWS_PASSWORD must be at least 12 characters in production"
                    )
                if credential.lower() in SettingsValidator.COMMON_TWS_PASSWORDS:
                    raise ValueError("TWS_PASSWORD cannot be a common/default password")
        return credential

    @staticmethod
    def validate_tws_credentials_required(
        tws_host: str | None,
        tws_port: int | None,
        tws_user: str | None,
        tws_password: str | None,
        tws_mock_mode: bool,
    ) -> None:
        """Validate that TWS credentials are provided when not in mock mode."""
        if not tws_mock_mode:
            required_credentials = {
                "tws_host": tws_host,
                "tws_port": tws_port,
                "tws_user": tws_user,
                "tws_password": tws_password,
            }
            missing = [k for k, v in required_credentials.items() if not v]
            if missing:
                raise ValueError(
                    f"TWS credentials required when not in mock mode: {missing}"
                )

    @classmethod
    def validate_all_pool_sizes(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate all connection pool sizes."""
        # Database pool validation
        if "db_pool_max_size" in values and "db_pool_min_size" in values:
            cls.validate_db_pool_sizes(
                values["db_pool_max_size"], values["db_pool_min_size"]
            )

        # Redis pool validation
        if "redis_pool_max_size" in values and "redis_pool_min_size" in values:
            cls.validate_redis_pool_sizes(
                values["redis_pool_max_size"], values["redis_pool_min_size"]
            )

        return values

    @classmethod
    def validate_production_security(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate security settings for production environment."""
        environment = values.get("environment")

        if environment == Environment.PRODUCTION:
            # Validate admin password
            if "admin_password" in values:
                cls.validate_production_password(
                    values["admin_password"], environment, "admin_password"
                )

            # Validate CORS
            if "cors_allowed_origins" in values:
                cls.validate_production_cors(
                    values["cors_allowed_origins"], environment
                )

            # Validate LLM API key
            if "llm_api_key" in values:
                cls.validate_llm_api_key_production(values["llm_api_key"], environment)

            # Validate TWS credentials
            if "tws_password" in values:
                cls.validate_tws_credentials_production(
                    values["tws_password"], environment, "tws_password"
                )

        return values

    @classmethod
    def validate_tws_configuration(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate TWS configuration consistency."""
        tws_mock_mode = values.get("tws_mock_mode", True)

        if not tws_mock_mode:
            cls.validate_tws_credentials_required(
                values.get("tws_host"),
                values.get("tws_port"),
                values.get("tws_user"),
                values.get("tws_password"),
                tws_mock_mode,
            )

        return values
