"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """App settings loaded from env."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./automeeting.db"

    # SMTP
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@example.com"
    smtp_use_tls: bool = True

    # App
    app_name: str = "谈话预约与查询管理系统"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
