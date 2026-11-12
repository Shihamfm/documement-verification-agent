import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "Institutional Clinical Document Verification System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT
    SECRET_KEY: str = "supersecret_jwt_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doc_verify_db"
    SQLITE_FALLBACK: bool = True
    SQLITE_DB_PATH: str = "data/verification.db"

    # Deduplication Window
    DUPLICATE_WINDOW_MINUTES: int = 5

    # Storage
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # AI / LLM
    LLM_PROVIDER: str = "groq"  # "groq", "offline_deterministic", "gemini", "openai", "ollama"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Embeddings
    EMBEDDING_PROVIDER: str = "tfidf_cosine"  # "tfidf_cosine", "gemini", "openai"

    # Default Seed Reviewer
    DEFAULT_ADMIN_EMAIL: str = "reviewer@meridianbay.org"
    DEFAULT_ADMIN_PASSWORD: str = "ReviewerPassword123!"
    DEFAULT_ADMIN_NAME: str = "Dr. Clinical Reviewer"


settings = Settings()
