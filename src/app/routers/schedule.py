"""
Роутер расписания и номера недели.
"""

from datetime import date
from typing import Any

from cachetools import TTLCache
from litestar import get
from litestar.exceptions import HTTPException

from litestar.params import Parameter
from typing import Annotated

from app.connectors import ScheduleConnector
from app.config import settings
from app.parsers import ICalParser
from app.schemas.schedule import ScheduleByNameResponse, ScheduleResponse
from app.schemas.search import ScheduleTarget

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


@get("/api/schedule/by-name")
async def get_schedule_by_name(
    q: Annotated[str, Parameter(query="query", description="Название группы, преподавателя или кабинета")],
    date_from: date | None = None,
    date_to: date | None = None,
    target: ScheduleTarget | None = None,
) -> ScheduleByNameResponse:
    """Получить расписание по названию — без предварительного поиска ID."""
    today = date.today()
    df = date_from or today
    dt = date_to or today

    connector = ScheduleConnector()
    raw = await connector.search(query=q, limit=15)

    results = raw.get("data", [])
    if target is not None:
        results = [r for r in results if r.get("scheduleTarget") == int(target)]

    if not results:
        raise HTTPException(status_code=404, detail=f"Ничего не найдено по запросу «{q}»")

    matched = results[0]
    entity_id: int = matched["id"]
    schedule_type: int = matched["scheduleTarget"]
    matched_target = ScheduleTarget(schedule_type)

    cache_key = (schedule_type, entity_id)
    if cache_key not in _ical_cache:
        ical_text = await connector.get_ical(schedule_type, entity_id)
        _ical_cache[cache_key] = ical_text
    else:
        ical_text = _ical_cache[cache_key]

    lessons = _parser.parse(ical_text, df, dt)

    return ScheduleByNameResponse(
        matched_id=entity_id,
        matched_title=matched["targetTitle"],
        matched_target=schedule_type,
        matched_target_name=matched_target.label,
        lessons=lessons,
        date_from=df,
        date_to=dt,
    )


@get("/api/week")
async def get_week() -> dict[str, Any]:
    """Получить номер текущей учебной недели."""
    connector = ScheduleConnector()
    return await connector.get_week_number()
