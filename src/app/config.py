from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings. Real environment variables take precedence over .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["local", "staging", "prod"] = "local"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/genai"
    jwt_secret: SecretStr


@lru_cache
def get_settings() -> Settings:
    # Cached so .env is read once per process; tests can override via
    # app.dependency_overrides[get_settings] or get_settings.cache_clear().
    return Settings()  # pyright: ignore[reportCallIssue]  # fields come from env
