from .base import Settings

class DevelopmentSettings(Settings):
    TWS_MOCK_MODE: bool = True
    # Override other settings for development if needed
    # For example, a local LLM endpoint
    # LLM_ENDPOINT: str = "http://localhost:8001/v1"
