from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (the directory holding .env), independent of the launch cwd.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """App settings. Real environment variables take precedence over .env."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["local", "staging", "prod"] = "local"
    log_level: str = "INFO"
    database_url: str ="postgresql+asyncpg://postgres:postgres@localhost:5432/genai"
    jwt_secret: SecretStr


@lru_cache
def get_settings() -> Settings:
    # Cached so .env is read once per process; tests can override via
    # app.dependency_overrides[get_settings] or get_settings.cache_clear().
    return Settings()  # pyright: ignore[reportCallIssue]  # fields come from env
