"""
Роутер расписания и номера недели.
"""

from datetime import date
from typing import Any

from cachetools import TTLCache
from litestar import get
from litestar.exceptions import HTTPException

from app.connectors import ScheduleConnector
from app.config import settings
from app.parsers import ICalParser
from app.schemas.schedule import ScheduleResponse

_ical_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.cache_ttl)
_parser = ICalParser()


@get("/api/schedule/{schedule_type:int}/{entity_id:int}")
async def get_schedule(
    schedule_type: int,
    entity_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ScheduleResponse:
    """Получить расписание для группы/преподавателя/кабинета."""
    today = date.today()
    df = date_from or today
    dt = date_to or today

    cache_key = (schedule_type, entity_id)
    if cache_key not in _ical_cache:
        connector = ScheduleConnector()
        ical_text = await connector.get_ical(schedule_type, entity_id)
        _ical_cache[cache_key] = ical_text
    else:
        ical_text = _ical_cache[cache_key]

    lessons = _parser.parse(ical_text, df, dt)

    return ScheduleResponse(
        lessons=lessons,
        date_from=df,
        date_to=dt,
    )


@get("/api/week")
async def get_week() -> dict[str, Any]:
    """Получить номер текущей учебной недели."""
    connector = ScheduleConnector()
    return await connector.get_week_number()
