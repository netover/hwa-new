from .base import Settings


class DevelopmentSettings(Settings):
    TWS_MOCK_MODE: bool = True
    TWS_VERIFY_SSL: bool = False  # SSL verification disabled for development
    # Cache hierarchy settings
    CACHE_HIERARCHY_L1_MAX_SIZE: int = 1000
    CACHE_HIERARCHY_L2_TTL: int = 300
    CACHE_HIERARCHY_L2_CLEANUP_INTERVAL: int = 30
    CACHE_HIERARCHY_NUM_SHARDS: int = 8
    CACHE_HIERARCHY_MAX_WORKERS: int = 4
    # Override other settings for development if needed
    # For example, a local LLM endpoint
    # LLM_ENDPOINT: str = "http://localhost:8001/v1"
