from .base import Settings


class ProductionSettings(Settings):
    # Production-optimized settings for 4M jobs/month environment

    # Cache optimizations for production scale
    CACHE_HIERARCHY_L1_MAX_SIZE: int = 10000  # 10K entries for high volume
    CACHE_HIERARCHY_L2_TTL: int = 900  # 15 minutes for production data
    CACHE_HIERARCHY_L2_CLEANUP_INTERVAL: int = 120  # 2 minutes cleanup
    CACHE_HIERARCHY_NUM_SHARDS: int = 12  # More shards for 15 users
    CACHE_HIERARCHY_MAX_WORKERS: int = 6  # More workers for production

    # TWS connection pool for production
    TWS_CACHE_TTL: int = 120  # 2 minutes cache for production

    # LLM budget for production scale (4M jobs/month)
    # Note: This would need to be set via environment variable
    # LLM_MONTHLY_BUDGET: float = 1000.0  # $1000/month for production

    # IA Auditor scheduler configuration for production
    # Reduce frequency to avoid overload in production
    IA_AUDITOR_FREQUENCY_HOURS: int = 6  # Every 6 hours instead of 2
    IA_AUDITOR_STARTUP_ENABLED: bool = False  # Don't run on startup in production

    # Override settings for production
    # TWS credentials MUST be set via environment variables in production
    # TWS_HOST: str = "your_prod_tws_host"
    # TWS_PORT: int = 31116
    # TWS_USER: str = "prod_user"
    # TWS_PASSWORD: str = "prod_password"

    TWS_VERIFY_SSL: bool = False  # SSL verification disabled as per project decision

    # Production LLM endpoint
    # LLM_ENDPOINT: str = "https://api.openai.com/v1"
    # LLM_API_KEY: str = "your_prod_openai_key"

    # Mem0 settings for production
    # MEM0_STORAGE_HOST: str = "your_prod_qdrant_host"
    # MEM0_STORAGE_PORT: int = 6333
