"""
AGSPE Configuration Module
Environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://agspe:agspe123@localhost:5432/agspe"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-strong-random-key"

    # API Keys (comma-separated)
    NEWS_API_KEYS: str = ""

    # Proxy (optional)
    PROXY_ROTATOR_URL: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Application
    APP_NAME: str = "AGSPE - Adani Group Strategic Prediction Engine"
    APP_VERSION: str = "1.0.0"
    APP_REPO: str = "https://github.com/cockroachparty/cockroachjanathaparty-agspe"
    DEBUG: bool = True

    # Rate Limiting
    CRAWL_DELAY_SECONDS: float = 2.0
    MAX_REQUESTS_PER_MINUTE: int = 30

    # Currency
    INR_TO_USD_RATE: float = 83.5

    # Validation thresholds
    VALIDATION_HIGH_THRESHOLD: float = 0.7
    VALIDATION_MEDIUM_THRESHOLD: float = 0.4

    # Cross-verification window (hours)
    CROSS_VERIFICATION_WINDOW_HOURS: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
