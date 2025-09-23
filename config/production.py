from .base import Settings

class ProductionSettings(Settings):
    # Override settings for production
    # TWS credentials MUST be set via environment variables in production
    # TWS_HOST: str = "your_prod_tws_host"
    # TWS_PORT: int = 31116
    # TWS_USER: str = "prod_user"
    # TWS_PASSWORD: str = "prod_password"

    # Ensure SSL verification is enabled in production
    # This would require modifying OptimizedTWSClient to use this setting
    # For now, it's a conceptual setting
    # TWS_VERIFY_SSL: bool = True

    # Production LLM endpoint
    # LLM_ENDPOINT: str = "https://api.openai.com/v1"
    # LLM_API_KEY: str = "your_prod_openai_key"

    # Mem0 settings for production
    # MEM0_STORAGE_HOST: str = "your_prod_qdrant_host"
    # MEM0_STORAGE_PORT: int = 6333
