"""
Схемы для поиска групп/преподавателей/кабинетов.
"""

from enum import IntEnum

from pydantic import BaseModel


class ScheduleTarget(IntEnum):
    GROUP = 1
    TEACHER = 2
    ROOM = 3

    @property
    def label(self) -> str:
        match self:
            case ScheduleTarget.GROUP:    return "Группа"
            case ScheduleTarget.TEACHER:  return "Преподаватель"
            case ScheduleTarget.ROOM:     return "Кабинет"


class SearchResultItem(BaseModel):
    id: int
    title: str
    full_title: str
    target: ScheduleTarget


class SearchResponse(BaseModel):
    data: list[SearchResultItem]
