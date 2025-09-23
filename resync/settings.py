from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from pydantic import BaseModel as AgnoSettings
from dotenv import load_dotenv
from pydantic import Field

# --- Environment Setup ---
# Load environment variables from .env file if it exists
env_path = Path(".") / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)

# --- Type Definitions ---
ModelEndpoint = str

# --- Base Settings Class (moved to config/base.py) ---
# This file will now load the correct settings class based on APP_ENV

APP_ENV = os.environ.get("APP_ENV", "development").lower()

if APP_ENV == "development":
    from config.development import DevelopmentSettings as CurrentSettings
elif APP_ENV == "production":
    from config.production import ProductionSettings as CurrentSettings
else:
    raise ValueError(f"Unknown APP_ENV: {APP_ENV}. Must be 'development' or 'production'.")

# --- Global Settings Instance ---
settings: CurrentSettings = CurrentSettings()