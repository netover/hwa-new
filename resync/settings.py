from __future__ import annotations

from pathlib import Path
from typing import Literal

from agno.settings import Settings as AgnoSettings
from pydantic import Field
from pydantic_settings import BaseSettings

# --- Type Definitions ---
# Define a union type for flexibility in specifying model endpoints
ModelEndpoint = str  # For now, just a string, can be a Union of Literals later
TWSProtocol = Literal["http", "https"]


# --- Core Application Settings ---
class Settings(AgnoSettings, BaseSettings):
    """
    Primary settings class for the Resync application.
    Inherits from Agno's and Pydantic's base settings for comprehensive configuration.
    """

    # --- Project Metadata ---
    PROJECT_NAME: str = "Resync"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Real-time monitoring dashboard for HCL Workload Automation"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # --- Agent and Model Configuration ---
    AGENT_CONFIG_PATH: Path = BASE_DIR / "config" / "runtime.json"

    # Configuration for the Language Model (LLM)
    LLM_MODEL_PATH: str = "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
    LLM_ENDPOINT: ModelEndpoint = "http://localhost:8001/v1"
    LLM_API_KEY: str = Field(description="API key for the LLM service.")
    LLM_N_GPU_LAYERS: int = -1

    # --- TWS Environment Configuration ---
    # These settings are critical for connecting to the HCL Workload Automation server
    # They MUST be provided in the .env file for security
    TWS_HOST: str = Field(description="Hostname or IP address of the TWS server.")
    TWS_PORT: int = Field(description="Port number for the TWS server connection.")
    TWS_USER: str = Field(description="Username for TWS authentication.")
    TWS_PASSWORD: str = Field(description="Password for TWS authentication.")
    TWS_PROTOCOL: TWSProtocol = Field(
        default="https",
        description="Protocol to use for TWS connection (http or https).",
    )
    TWS_SSL_VERIFY: bool = Field(
        default=True,
        description="Enable or disable SSL certificate verification for TWS connection.",
    )
    TWS_ENGINE_NAME: str = "tws-engine"
    TWS_ENGINE_OWNER: str = "tws-owner"

    class Config:
        """
        Pydantic model configuration.
        Specifies the path to the .env file for loading environment variables.
        """

        env_file: str = ".env"
        env_file_encoding: str = "utf-8"
        extra: str = "ignore"  # Allow extra fields without raising an error


# --- Global Settings Instance ---
# Create a single, importable instance of the settings
settings = Settings()
