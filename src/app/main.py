"""
Точка входа Litestar-приложения.
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from app.config import settings
from app.connectors import ScheduleConnector
from app.routers import get_schedule, get_schedule_by_name, get_week, search

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    yield
    await ScheduleConnector().shutdown()


app = Litestar(
    route_handlers=[search, get_schedule, get_schedule_by_name, get_week],
    lifespan=[lifespan],
    openapi_config=OpenAPIConfig(
        title=settings.app_title,
        version=settings.app_version,
    ),
)
