"""
Точка входа для локального запуска.
Читает PORT и DEBUG из .env / переменных окружения.
"""

import sys
sys.path.insert(0, "src")

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
