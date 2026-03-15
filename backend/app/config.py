"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union


def parse_list(v: Union[str, List[str]]) -> List[str]:
    """Parse comma-separated string to list."""
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return []


class Settings(BaseSettings):
    """App settings loaded from env."""

    # Database - defaults to SQLite for local development, override with DATABASE_URL env var
    database_url: str = "sqlite+aiosqlite:///./automeeting.db"

    # Database connection pool settings (for PostgreSQL)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # CORS settings - accepts comma-separated string or list
    cors_origins: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"
    cors_allow_credentials: bool = True

    # SMTP
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@example.com"
    smtp_use_tls: bool = True

    # App
    app_name: str = "谈话预约与查询管理系统"

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list."""
        return parse_list(self.cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
