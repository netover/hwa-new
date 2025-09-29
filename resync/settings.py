from __future__ import annotations

import os
from pathlib import Path
from dynaconf import Dynaconf

# --- Dynamic Configuration with Dynaconf ---
# Load settings from TOML files and environment variables
settings = Dynaconf(
    envvar_prefix="APP",  # Prefix for environment variables (e.g., APP_TWS_HOST)
    settings_files=[
        "settings.toml",  # Base settings
        f"settings.{os.environ.get('APP_ENV', 'development')}.toml"  # Environment-specific overrides
    ],
    environments=True,  # Enable environment-specific loading
    load_dotenv=False,  # Disable automatic .env loading for CI/CD compatibility
    env_switcher="APP_ENV",  # Use APP_ENV to switch environments
)

# --- Type Definitions (for backward compatibility) ---
ModelEndpoint = str

# Post-process settings for type conversion and dynamic path resolution
# Set BASE_DIR dynamically based on current working directory if not already set
if not hasattr(settings, 'BASE_DIR') or not settings.BASE_DIR:
    # Use current working directory as base
    current_dir = Path.cwd()
    settings.BASE_DIR = current_dir

# Ensure BASE_DIR is a Path object and resolve to absolute path
settings.BASE_DIR = Path(settings.BASE_DIR).resolve()
