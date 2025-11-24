"""Configuration helpers for the Google Play Reviews framework."""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    google_service_account_file: str = "TODO_PATH_TO_SERVICE_ACCOUNT_JSON"
    google_play_scopes: List[str] = [
        "https://www.googleapis.com/auth/androidpublisher",
    ]
    default_package_name: str = "com.example.app"
    default_translation_language: Optional[str] = None
    default_page_size: int = 50
    cache_ttl_seconds: int = 300
    ai_provider: Optional[str] = None
    openai_api_key: Optional[str] = None
    enable_mock_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
