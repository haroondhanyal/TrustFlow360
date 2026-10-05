from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://trustflow:trustflow_dev@localhost:5432/trustflow"
    jwt_secret: str = "development-only-change-this-secret"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("jwt_secret")
    @classmethod
    def require_secure_production_secret(cls, value: str, info):
        if info.data.get("app_env") == "production" and len(value) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters in production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
