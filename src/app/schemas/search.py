"""
Схемы для поиска групп/преподавателей/кабинетов.
"""

from enum import IntEnum

from pydantic import BaseModel


class ScheduleTarget(IntEnum):
    GROUP = 1
    TEACHER = 2
    ROOM = 3


class SearchResultItem(BaseModel):
    id: int
    title: str
    full_title: str
    target: ScheduleTarget


class SearchResponse(BaseModel):
    data: list[SearchResultItem]
