from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Variáveis de ambiente
    MODEL_PATH: str = "/models/gemma-2b-it-GGUF.Q4_K_M.gguf"  # Caminho do modelo Gemma
    TWS_HOST: str = "https://tws-master:31116"  # URL base TWS
    TWS_USERNAME: str = "readonly"
    TWS_PASSWORD: str = "readonly"
    OPENROUTER_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    APP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"
    LLM_PROVIDER: str = "openrouter"  # ou openai, local, etc.
    ENABLE_MODEL_DISCOVERY: bool = True
    TWS_MOCK_MODE: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
