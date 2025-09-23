from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel as AgnoSettings
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
    AUDITOR_MODEL_NAME: str = Field(
        default=os.environ.get("AUDITOR_MODEL_NAME", "gpt-4o-mini"),
        description="Model to be used by the IA Auditor.",
    )
    LLM_N_GPU_LAYERS: int = Field(
        default=int(os.environ.get("LLM_N_GPU_LAYERS", -1)),
        description="Number of GPU layers to offload (-1 for all).",
    )

    # --- Knowledge Graph (Mem0) Configuration ---
    MEM0_EMBEDDING_PROVIDER: str = Field(default=os.environ.get("MEM0_EMBEDDING_PROVIDER", "openai"))
    MEM0_EMBEDDING_MODEL: str = Field(default=os.environ.get("MEM0_EMBEDDING_MODEL", "text-embedding-3-small"))
    MEM0_LLM_PROVIDER: str = Field(default=os.environ.get("MEM0_LLM_PROVIDER", "openai"))
    MEM0_LLM_MODEL: str = Field(default=os.environ.get("MEM0_LLM_MODEL", "gpt-4o-mini"))
    MEM0_STORAGE_PROVIDER: str = Field(default=os.environ.get("MEM0_STORAGE_PROVIDER", "qdrant"))
    MEM0_STORAGE_HOST: str = Field(default=os.environ.get("MEM0_STORAGE_HOST", "localhost"))
    MEM0_STORAGE_PORT: int = Field(default=int(os.environ.get("MEM0_STORAGE_PORT", 6333)))
    # --- Redis Configuration (for Audit Queue) ---
    REDIS_URL: str = Field(
        default=os.environ.get("REDIS_URL", "redis://localhost:6379"),
        description="Redis connection URL for audit queue and caching.",
    )



    # --- TWS Environment Configuration ---
    TWS_MOCK_MODE: bool = Field(
        default=bool(os.environ.get("TWS_MOCK_MODE", False)),
        description="Enable mock mode for TWS client to use local data instead of a live connection.",
    )
    TWS_CACHE_TTL: int = Field(
        default=int(os.environ.get("TWS_CACHE_TTL", 60)), # Default to 60 seconds
        description="Time-To-Live (TTL) for TWS API responses in cache (in seconds).",
    )
    # These settings are critical for connecting to the HCL Workload Automation server
    # They MUST be provided in the .env file for security
    TWS_HOST: str = Field(default="", description="Hostname or IP address of the TWS server.")
    TWS_PORT: int = Field(default=31111, description="Port number for the TWS server connection.")
    TWS_USER: str = Field(default="", description="Username for TWS authentication.")
    TWS_PASSWORD: str = Field(default="", description="Password for TWS authentication.")
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