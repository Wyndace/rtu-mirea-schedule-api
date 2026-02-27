"""
Вспомогательные типы.
"""

from datetime import date, datetime
from typing import Annotated

from pydantic import BeforeValidator


def _parse_date(value: object) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError(f"Ожидалась строка, получено {type(value).__name__!r}")
    for fmt in ("%d.%m.%y", "%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Неверный формат даты: {value!r}. "
        "Поддерживаются: ДД.ММ.ГГ, ДД.ММ.ГГГГ, ГГГГ-ММ-ДД"
    )


# date, который принимает ДД.ММ.ГГ, ДД.ММ.ГГГГ и ГГГГ-ММ-ДД
FlexDate = Annotated[date, BeforeValidator(_parse_date)]


def parse_date_param(value: str | None, default: date) -> date:
    """Парсит строку даты в нескольких форматах; если None — возвращает default."""
    if value is None:
        return default
    try:
        return _parse_date(value)
    except ValueError as e:
        from litestar.exceptions import HTTPException
        raise HTTPException(status_code=400, detail=str(e)) from e
