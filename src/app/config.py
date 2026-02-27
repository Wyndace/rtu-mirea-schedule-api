"""
Конфигурация приложения.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "RTU MIREA Schedule API"
    app_version: str = "1.0.0"
    # DEBUG=true включает уровень логирования DEBUG (подробные логи каждого HTTP запроса/ответа)
    # и режим reload в uvicorn при локальном запуске через runserver.py
    debug: bool = False
    port: int = 8000
    cache_ttl: int = 3600  # секунд

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
