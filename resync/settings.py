from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dynaconf import Dynaconf
from pydantic import BaseModel, Field, validator, field_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings

from resync.core.exceptions import ConfigurationError

# --- Dynamic Configuration with Dynaconf ---
# Load settings from TOML files and environment variables
settings_dynaconf = Dynaconf(
    envvar_prefix="APP",  # Prefix for environment variables (e.g., APP_TWS_HOST)
    settings_files=[
        "settings.toml",  # Base settings
        f"settings.{os.environ.get('APP_ENV', 'development')}.toml",  # Environment-specific overrides
    ],
    environments=True,  # Enable environment-specific loading
    load_dotenv=False,  # Disable automatic .env loading for CI/CD compatibility
    env_switcher="APP_ENV",  # Use APP_ENV to switch environments
)

# --- Type Definitions (for backward compatibility) ---
ModelEndpoint = str


class BaseSettings(PydanticBaseSettings):
    """Base settings class with environment-specific validation."""
    
    environment: str = Field(default="development", env="APP_ENV")
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        allowed_environments = ["development", "production", "test"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v


class ApplicationSettings(BaseSettings):
    """Pydantic model for application settings with validation."""
    
    # Database settings
    neo4j_uri: str = Field(..., env="NEO4J_URI")
    neo4j_user: str = Field(..., env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    
    # Redis settings
    redis_url: str = Field(..., env="REDIS_URL")
    redis_min_connections: int = Field(default=1, env="REDIS_MIN_CONNECTIONS")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    redis_timeout: float = Field(default=30.0, env="REDIS_TIMEOUT")
    
    # LLM settings
    llm_endpoint: str = Field(..., env="LLM_ENDPOINT")
    llm_api_key: str = Field(..., env="LLM_API_KEY")
    
    # Admin credentials
    admin_username: str = Field(..., env="ADMIN_USERNAME")
    admin_password: str = Field(..., env="ADMIN_PASSWORD")
    
    # TWS settings
    tws_mock_mode: bool = Field(default=False, env="TWS_MOCK_MODE")
    tws_host: Optional[str] = Field(default=None, env="TWS_HOST")
    tws_port: Optional[int] = Field(default=None, env="TWS_PORT")
    tws_user: Optional[str] = Field(default=None, env="TWS_USER")
    tws_password: Optional[str] = Field(default=None, env="TWS_PASSWORD")
    
    # Security settings
    cors_allowed_origins: list[str] = Field(default=["*"], env="CORS_ALLOWED_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Base directory
    base_dir: Path = Field(default=Path.cwd(), env="BASE_DIR")
    
    @field_validator('tws_port')
    @classmethod
    def validate_tws_port(cls, v):
        if v is not None:
            if not 1 <= v <= 65535:
                raise ValueError('TWS port must be between 1 and 65535')
        return v

    @field_validator('redis_min_connections', 'redis_max_connections')
    @classmethod
    def validate_connection_counts(cls, v):
        if v < 0:
            raise ValueError('Connection count must be non-negative')
        return v

    @field_validator('redis_timeout')
    @classmethod
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


def load_config() -> ApplicationSettings:
    """
    Enhanced configuration loading with environment-specific validation.
    
    Returns:
        ApplicationSettings instance with loaded and validated settings
    """
    try:
        app_settings = ApplicationSettings()
        
        # Additional validation specific to the application
        if not app_settings.tws_mock_mode:
            if not app_settings.tws_host:
                raise ConfigurationError("TWS_HOST is required when not in mock mode")
            if not app_settings.tws_port:
                raise ConfigurationError("TWS_PORT is required when not in mock mode")
            if not app_settings.tws_user:
                raise ConfigurationError("TWS_USER is required when not in mock mode")
            if not app_settings.tws_password:
                raise ConfigurationError("TWS_PASSWORD is required when not in mock mode")
        
        # Perform environment-specific validation
        if app_settings.environment == "production":
            # In production, require secure CORS settings
            if "*" in app_settings.cors_allowed_origins:
                raise ConfigurationError("Wildcard CORS origins are not allowed in production")
            
            if app_settings.cors_allow_credentials and "*" in app_settings.cors_allow_origins:
                raise ConfigurationError("Allowing credentials with wildcard CORS origins is insecure in production")
            
            # In production, ensure redis connection pool is appropriately sized
            if app_settings.redis_max_connections < 5:
                raise ConfigurationError("Redis max connections should be at least 5 in production")
        
        return app_settings
    except Exception as e:
        raise ConfigurationError(f"Configuration error: {str(e)}") from e


# Load settings using the new Pydantic-based configuration
settings = load_config()

# Post-process settings for type conversion and dynamic path resolution
# Set BASE_DIR dynamically based on current working directory if not already set
if not hasattr(settings_dynaconf, "BASE_DIR") or not settings_dynaconf.BASE_DIR:
    # Use current working directory as base
    current_dir = Path.cwd()
    settings_dynaconf.BASE_DIR = current_dir

# Ensure BASE_DIR is a Path object and resolve to absolute path
settings_dynaconf.BASE_DIR = Path(settings_dynaconf.BASE_DIR).resolve()


def validate_settings(config) -> None:
    """
    Validates that all critical settings are present and not empty.
    This ensures the application fails fast at startup if misconfigured.

    Args:
        config: The settings object (either dynaconf or pydantic based).

    Raises:
        ConfigurationError: If a required setting is missing or empty.
    """
    # Get values from either dynaconf or pydantic settings
    def get_value(key):
        if hasattr(config, key.lower()):
            return getattr(config, key.lower())
        elif hasattr(config, key):
            return getattr(config, key)
        else:
            # Fallback to dynaconf-style access
            return getattr(settings_dynaconf, key, None)

    required_keys = [
        "NEO4J_URI",
        "NEO4J_USER", 
        "NEO4J_PASSWORD",
        "REDIS_URL",
        "LLM_ENDPOINT",
        "LLM_API_KEY",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
    ]

    # TWS credentials are only required if not in mock mode.
    tws_mock_mode = get_value("TWS_MOCK_MODE")
    if tws_mock_mode is None or not tws_mock_mode:
        required_keys.extend(["TWS_HOST", "TWS_PORT", "TWS_USER", "TWS_PASSWORD"])

    missing_keys = [key for key in required_keys if not get_value(key)]

    if missing_keys:
        raise ConfigurationError(
            f"Missing or empty required settings: {', '.join(missing_keys)}. "
            "Please check your .env file or environment variables."
        )

    # Validate that sensitive values are not default/placeholder values
    validations = [
        ("LLM_API_KEY", lambda x: x and x != "your_default_api_key_here", "LLM_API_KEY must be set to a valid API key"),
        ("ADMIN_USERNAME", lambda x: x and x != "admin", "ADMIN_USERNAME must be changed from default"),
        ("ADMIN_PASSWORD", lambda x: x and x != "admin", "ADMIN_PASSWORD must be changed from default"),
        ("NEO4J_PASSWORD", lambda x: x and x != "password", "NEO4J_PASSWORD must be changed from default"),
    ]

    for field_name, validation_func, error_msg in validations:
        value = get_value(field_name)
        if not validation_func(value):
            raise ConfigurationError(error_msg)


# Run validation immediately after loading settings
validate_settings(settings)
