# backend/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # ── Application ─────────────────────────────────────────
    APP_NAME: str = "BizRithm"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "bizrithm-super-secret"
    ALLOWED_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    # ── Database ────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://bizrithm:bizrithm123@localhost:5432/bizrithm_db"
    DATABASE_URL_SYNC: str = "postgresql://bizrithm:bizrithm123@localhost:5432/bizrithm_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    CACHE_TTL_SECONDS: int = 3600

    # ── AI / LLM ─────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-1.5-flash-latest"
    OPENAI_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 4096

    # ── JWT ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "bizrithm-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── File Storage ─────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: str = "csv,xlsx,xls,json"
    REPORTS_DIR: str = "./reports/generated"
    CHARTS_DIR: str = "./reports/charts"

    # ── ML ───────────────────────────────────────────────────
    ML_MODELS_DIR: str = "./ml_models/saved"
    ENABLE_LSTM: bool = False
    DEFAULT_FORECAST_PERIODS: int = 30

    # ── Logging ──────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/bizrithm.log"

    # ── Rate Limiting ────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip() for e in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
