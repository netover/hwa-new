"""
RAG Microservice Configuration

This module defines the Settings class for the RAG microservice, including service,
job queue, RAG, processing, and logging configurations.
"""

import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Base directory configuration
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent

    # Service configuration
    SERVICE_NAME: str = "RAG Microservice"
    SERVICE_VERSION: str = "1.0.0"
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Job queue configuration (SQLite-based)
    JOB_QUEUE_DB_PATH: str = os.getenv("JOB_QUEUE_DB_PATH", "job_queue.db")

    # RAG configuration
    RAG_KNOWLEDGE_BASE_DIR: str = os.getenv("RAG_KNOWLEDGE_BASE_DIR", "../RAG/BASE")

    # Vector store configuration
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")  # "faiss" or "chroma"
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Text processing configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))

    # Processing configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 100))
    MAX_CONCURRENT_PROCESSES: int = int(os.getenv("MAX_CONCURRENT_PROCESSES", 1))  # CPU-only constraint

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Knowledge base and protected directories (copied from main project)
    KNOWLEDGE_BASE_DIRS: list[Path] = [
        Path(RAG_KNOWLEDGE_BASE_DIR)
    ]

    PROTECTED_DIRECTORIES: list[Path] = [
        Path(RAG_KNOWLEDGE_BASE_DIR) / "BASE"
    ]

    # Add missing fields from the main project's settings
    # These are needed to avoid validation errors
    admin_username: str = ""
    admin_password: str = ""
    debug: bool = False
    database_url: str = ""
    secret_key: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""
    llm_endpoint: str = ""
    llm_api_key: str = ""

    class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"  # Allow extra fields from environment

settings = Settings()