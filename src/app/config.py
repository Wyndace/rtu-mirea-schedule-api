"""
Конфигурация приложения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "RTU MIREA Schedule API"
    app_version: str = "1.0.0"
    debug: bool = False
    cache_ttl: int = 3600  # секунд

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
