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
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # Cache settings
    async_cache_ttl: int = Field(default=60, env="ASYNC_CACHE_TTL", description="Time-to-live for cache entries in seconds")
    async_cache_cleanup_interval: int = Field(default=30, env="ASYNC_CACHE_CLEANUP_INTERVAL", description="How often to run background cleanup in seconds")
    async_cache_num_shards: int = Field(default=16, env="ASYNC_CACHE_NUM_SHARDS", description="Number of shards for the lock")
    async_cache_enable_wal: bool = Field(default=False, env="ASYNC_CACHE_ENABLE_WAL", description="Whether to enable Write-Ahead Logging for persistence")
    async_cache_wal_path: Optional[str] = Field(default=None, env="ASYNC_CACHE_WAL_PATH", description="Path for WAL files")
    async_cache_max_entries: int = Field(default=100000, env="ASYNC_CACHE_MAX_ENTRIES", description="Maximum number of entries in cache")
    async_cache_max_memory_mb: int = Field(default=100, env="ASYNC_CACHE_MAX_MEMORY_MB", description="Maximum memory usage in MB")
    async_cache_paranoia_mode: bool = Field(default=False, env="ASYNC_CACHE_PARANOIA_MODE", description="Enable paranoid operational mode with lower bounds")

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_min_connections: int = Field(default=1, env="REDIS_MIN_CONNECTIONS")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    redis_timeout: float = Field(default=30.0, env="REDIS_TIMEOUT")

    # LLM settings
    llm_endpoint: str = Field(default="http://localhost:11434/v1", env="LLM_ENDPOINT")
    llm_api_key: str = Field(default="dummy_key_for_development", env="LLM_API_KEY")

    # Admin credentials
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password: str = Field(default="change_me_please", env="ADMIN_PASSWORD")
    
    # TWS settings
    tws_mock_mode: bool = Field(default=True, env="TWS_MOCK_MODE")
    tws_host: Optional[str] = Field(default=None, env="TWS_HOST")
    tws_port: Optional[int] = Field(default=None, env="TWS_PORT")
    tws_user: Optional[str] = Field(default=None, env="TWS_USER")
    tws_password: Optional[str] = Field(default=None, env="TWS_PASSWORD")
    
    # Security settings
    cors_allowed_origins: list[str] = Field(default=["*"], env="CORS_ALLOWED_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Server settings
    server_host: str = Field(default="127.0.0.1", env="SERVER_HOST")  # Secure default: localhost only
    server_port: int = Field(default=8000, env="SERVER_PORT")
    
    # Base directory
    base_dir: Path = Field(default=Path.cwd(), env="BASE_DIR")

    # Additional settings from dynaconf
    project_name: str = Field(default="Resync", env="PROJECT_NAME")
    project_version: str = Field(default="1.0.0", env="PROJECT_VERSION")
    description: str = Field(default="Real-time monitoring dashboard for HCL Workload Automation", env="DESCRIPTION")

    # Model names
    auditor_model_name: str = Field(default="gpt-3.5-turbo", env="AUDITOR_MODEL_NAME")
    agent_model_name: str = Field(default="gpt-4o", env="AGENT_MODEL_NAME")

    # Connection pool settings
    db_pool_min_size: int = Field(default=20, env="DB_POOL_MIN_SIZE")
    db_pool_max_size: int = Field(default=100, env="DB_POOL_MAX_SIZE")
    db_pool_idle_timeout: int = Field(default=1200, env="DB_POOL_IDLE_TIMEOUT")
    db_pool_connect_timeout: int = Field(default=60, env="DB_POOL_CONNECT_TIMEOUT")
    db_pool_health_check_interval: int = Field(default=60, env="DB_POOL_HEALTH_CHECK_INTERVAL")
    db_pool_max_lifetime: int = Field(default=1800, env="DB_POOL_MAX_LIFETIME")

    redis_pool_min_size: int = Field(default=5, env="REDIS_POOL_MIN_SIZE")
    redis_pool_max_size: int = Field(default=20, env="REDIS_POOL_MAX_SIZE")
    redis_pool_idle_timeout: int = Field(default=300, env="REDIS_POOL_IDLE_TIMEOUT")
    redis_pool_connect_timeout: int = Field(default=30, env="REDIS_POOL_CONNECT_TIMEOUT")
    redis_pool_health_check_interval: int = Field(default=60, env="REDIS_POOL_HEALTH_CHECK_INTERVAL")
    redis_pool_max_lifetime: int = Field(default=1800, env="REDIS_POOL_MAX_LIFETIME")

    http_pool_min_size: int = Field(default=10, env="HTTP_POOL_MIN_SIZE")
    http_pool_max_size: int = Field(default=100, env="HTTP_POOL_MAX_SIZE")
    http_pool_idle_timeout: int = Field(default=300, env="HTTP_POOL_IDLE_TIMEOUT")
    http_pool_connect_timeout: int = Field(default=10, env="HTTP_POOL_CONNECT_TIMEOUT")
    http_pool_health_check_interval: int = Field(default=60, env="HTTP_POOL_HEALTH_CHECK_INTERVAL")
    http_pool_max_lifetime: int = Field(default=1800, env="HTTP_POOL_MAX_LIFETIME")

    tws_base_url: str = Field(default="http://localhost:31111", env="TWS_BASE_URL")
    database_url: str = Field(default="sqlite:///./test.db", env="DATABASE_URL")

    # Rate limiting settings
    rate_limit_public_per_minute: int = Field(default=100, env="RATE_LIMIT_PUBLIC_PER_MINUTE")
    rate_limit_authenticated_per_minute: int = Field(default=1000, env="RATE_LIMIT_AUTHENTICATED_PER_MINUTE")
    rate_limit_critical_per_minute: int = Field(default=50, env="RATE_LIMIT_CRITICAL_PER_MINUTE")
    rate_limit_error_handler_per_minute: int = Field(default=15, env="RATE_LIMIT_ERROR_HANDLER_PER_MINUTE")
    rate_limit_websocket_per_minute: int = Field(default=30, env="RATE_LIMIT_WEBSOCKET_PER_MINUTE")
    rate_limit_dashboard_per_minute: int = Field(default=10, env="RATE_LIMIT_DASHBOARD_PER_MINUTE")
    rate_limit_storage_uri: str = Field(default="redis://localhost:6379", env="RATE_LIMIT_STORAGE_URI")
    rate_limit_key_prefix: str = Field(default="resync:ratelimit:", env="RATE_LIMIT_KEY_PREFIX")
    rate_limit_sliding_window: bool = Field(default=True, env="RATE_LIMIT_SLIDING_WINDOW")

    @property
    def BASE_DIR(self):
        """Backward compatibility property for dynaconf-style access."""
        return self.base_dir

    @property
    def PROJECT_NAME(self):
        """Backward compatibility property for dynaconf-style access."""
        return self.project_name

    @property
    def PROJECT_VERSION(self):
        """Backward compatibility property for dynaconf-style access."""
        return self.project_version

    @property
    def DESCRIPTION(self):
        """Backward compatibility property for dynaconf-style access."""
        return self.description

    # Model name properties
    @property
    def AUDITOR_MODEL_NAME(self):
        return self.auditor_model_name

    @property
    def AGENT_MODEL_NAME(self):
        return self.agent_model_name

    # Connection pool properties
    @property
    def DB_POOL_MIN_SIZE(self):
        return self.db_pool_min_size

    @property
    def DB_POOL_MAX_SIZE(self):
        return self.db_pool_max_size

    @property
    def DB_POOL_IDLE_TIMEOUT(self):
        return self.db_pool_idle_timeout

    @property
    def DB_POOL_CONNECT_TIMEOUT(self):
        return self.db_pool_connect_timeout

    @property
    def DB_POOL_HEALTH_CHECK_INTERVAL(self):
        return self.db_pool_health_check_interval

    @property
    def DB_POOL_MAX_LIFETIME(self):
        return self.db_pool_max_lifetime

    @property
    def REDIS_POOL_MIN_SIZE(self):
        return self.redis_pool_min_size

    @property
    def REDIS_POOL_MAX_SIZE(self):
        return self.redis_pool_max_size

    @property
    def REDIS_POOL_IDLE_TIMEOUT(self):
        return self.redis_pool_idle_timeout

    @property
    def REDIS_POOL_CONNECT_TIMEOUT(self):
        return self.redis_pool_connect_timeout

    @property
    def REDIS_POOL_HEALTH_CHECK_INTERVAL(self):
        return self.redis_pool_health_check_interval

    @property
    def REDIS_POOL_MAX_LIFETIME(self):
        return self.redis_pool_max_lifetime

    @property
    def HTTP_POOL_MIN_SIZE(self):
        return self.http_pool_min_size

    @property
    def HTTP_POOL_MAX_SIZE(self):
        return self.http_pool_max_size

    @property
    def HTTP_POOL_IDLE_TIMEOUT(self):
        return self.http_pool_idle_timeout

    @property
    def HTTP_POOL_CONNECT_TIMEOUT(self):
        return self.http_pool_connect_timeout

    @property
    def HTTP_POOL_HEALTH_CHECK_INTERVAL(self):
        return self.http_pool_health_check_interval

    @property
    def HTTP_POOL_MAX_LIFETIME(self):
        return self.http_pool_max_lifetime

    @property
    def TWS_BASE_URL(self):
        return self.tws_base_url

    def __getattr__(self, name: str):
        """Automatically convert uppercase attribute access to lowercase field access for backward compatibility."""
        # Convert UPPER_CASE to lower_case
        if name.isupper() and '_' in name:
            lower_name = name.lower()
            if hasattr(self, lower_name):
                return getattr(self, lower_name)
        # If not found, raise AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

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
        extra = "allow"


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
    # For development environment, allow some default values
    environment = get_value("APP_ENV") or "development"
    is_production = environment == "production"

    validations = [
        ("LLM_API_KEY", lambda x: x and x != "your_default_api_key_here", "LLM_API_KEY must be set to a valid API key"),
        ("ADMIN_USERNAME", lambda x: x and (not is_production or x != "admin"), "ADMIN_USERNAME must be changed from default in production"),
        ("ADMIN_PASSWORD", lambda x: x and (not is_production or x != "admin"), "ADMIN_PASSWORD must be changed from default in production"),
        ("NEO4J_PASSWORD", lambda x: x and (not is_production or x != "password"), "NEO4J_PASSWORD must be changed from default in production"),
    ]

    for field_name, validation_func, error_msg in validations:
        value = get_value(field_name)
        if not validation_func(value):
            raise ConfigurationError(error_msg)


# Run validation immediately after loading settings
validate_settings(settings)
