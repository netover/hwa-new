from __future__ import annotations

import os
from pathlib import Path

from agno.settings import Settings as AgnoSettings
from dotenv import load_dotenv
from pydantic import Field

# --- Environment Setup ---
# Load environment variables from .env file if it exists
# This is crucial for local development and testing
env_path = Path(".") / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)

# --- Type Definitions ---
# Define a union type for flexibility in specifying model endpoints
ModelEndpoint = str  # For now, just a string, can be a Union of Literals later


# --- Core Application Settings ---
class Settings(AgnoSettings):
    """
    Primary settings class for the Resync application.
    Inherits from Agno's base settings and adds application-specific configurations.
    """

    # --- Project Metadata ---
    PROJECT_NAME: str = "Resync"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Real-time monitoring dashboard for HCL Workload Automation"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # --- Agent and Model Configuration ---
    # Path to the agent configuration file
    AGENT_CONFIG_PATH: Path = BASE_DIR / "config" / "runtime.json"

    # Configuration for the Language Model (LLM)
    # Using Field for default values and clear documentation
    LLM_MODEL_PATH: str = Field(
        default=os.environ.get("LLM_MODEL_PATH", "models/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"),
        description="Path to the GGUF model file for the LLM.",
    )
    LLM_ENDPOINT: ModelEndpoint = Field(
        default=os.environ.get("LLM_ENDPOINT", "http://localhost:8001/v1"),
        description="Endpoint for the LLM API.",
    )
    LLM_API_KEY: str = Field(
        default=os.environ.get("LLM_API_KEY", "your_default_api_key_here"),
        description="API key for the LLM service.",
    )
    LLM_N_GPU_LAYERS: int = Field(
        default=int(os.environ.get("LLM_N_GPU_LAYERS", -1)),
        description="Number of GPU layers to offload (-1 for all).",
    )

    # --- TWS Environment Configuration ---
    # These settings are critical for connecting to the HCL Workload Automation server
    # They MUST be provided in the .env file for security
    TWS_HOST: str = Field(description="Hostname or IP address of the TWS server.")
    TWS_PORT: int = Field(description="Port number for the TWS server connection.")
    TWS_USER: str = Field(description="Username for TWS authentication.")
    TWS_PASSWORD: str = Field(description="Password for TWS authentication.")
    TWS_ENGINE_NAME: str = Field(
        default="tws-engine", description="Name of the TWS engine to connect to."
    )
    TWS_ENGINE_OWNER: str = Field(
        default="tws-owner", description="Owner of the TWS engine."
    )

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
