from __future__ import annotations

import os
from pathlib import Path
from dynaconf import Dynaconf

from resync.core.exceptions import ConfigurationError

# --- Dynamic Configuration with Dynaconf ---
# Load settings from TOML files and environment variables
settings = Dynaconf(
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

# Post-process settings for type conversion and dynamic path resolution
# Set BASE_DIR dynamically based on current working directory if not already set
if not hasattr(settings, "BASE_DIR") or not settings.BASE_DIR:
    # Use current working directory as base
    current_dir = Path.cwd()
    settings.BASE_DIR = current_dir

# Ensure BASE_DIR is a Path object and resolve to absolute path
settings.BASE_DIR = Path(settings.BASE_DIR).resolve()


def validate_settings(config: Dynaconf) -> None:
    """
    Validates that all critical settings are present and not empty.
    This ensures the application fails fast at startup if misconfigured.

    Args:
        config: The Dynaconf settings object.

    Raises:
        ConfigurationError: If a required setting is missing or empty.
    """
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
    if not config.get("TWS_MOCK_MODE", False):
        required_keys.extend(["TWS_HOST", "TWS_PORT", "TWS_USER", "TWS_PASSWORD"])

    # Admin credentials must be explicitly defined - no insecure defaults allowed
    # This prevents default admin/admin credentials in production environments
    # Check for placeholder values that indicate insecure defaults
    placeholder_checks = {
        "LLM_API_KEY": "your_default_api_key_here",
        "JWT_SECRET_KEY": "dummy-secret-key"  # This comes from the OAuth2 file
    }
    
    for setting_name, placeholder_value in placeholder_checks.items():
        current_value = config.get(setting_name)
        if current_value and current_value == placeholder_value:
            raise ConfigurationError(
                f"Setting '{setting_name}' is using an insecure default value. "
                f"Please provide a proper value for production use."
            )

    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        raise ConfigurationError(
            f"Missing or empty required settings: {', '.join(missing_keys)}. "
            "Please check your .env file or environment variables."
        )


# Run validation immediately after loading settings
validate_settings(settings)