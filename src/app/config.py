from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (the directory holding .env), independent of the launch cwd.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

MIN_JWT_SECRET_LEN = 32


class Settings(BaseSettings):
    """App settings. Real environment variables take precedence over .env."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["local", "staging", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    # No default on purpose: a missing DATABASE_URL must fail at startup, not
    # silently fall back to localhost with a well-known password.
    database_url: str
    jwt_secret: SecretStr

    @model_validator(mode="after")
    def _require_strong_secret_outside_local(self) -> "Settings":
        # 32 bytes is the HS256 recommended minimum (RFC 7518 s3.2).
        if (
            self.app_env != "local"
            and len(self.jwt_secret.get_secret_value()) < MIN_JWT_SECRET_LEN
        ):
            raise ValueError(
                f"jwt_secret must be at least {MIN_JWT_SECRET_LEN} characters when app_env != 'local'"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    # Cached so .env is read once per process; tests can override via
    # app.dependency_overrides[get_settings] or get_settings.cache_clear().
    return Settings()  # pyright: ignore[reportCallIssue]  # fields come from env
