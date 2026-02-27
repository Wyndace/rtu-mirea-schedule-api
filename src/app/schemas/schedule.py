"""
Схемы для расписания.
"""

from datetime import date

from pydantic import BaseModel


class PersonRef(BaseModel):
    id: int
    name: str


class RoomRef(BaseModel):
    id: int
    number: str
    campus: str


class Lesson(BaseModel):
    date: date
    time_start: str       # "09:00"
    time_end: str         # "10:30"
    discipline: str
    lesson_type: str      # "ПР"
    lesson_type_full: str  # "Практические занятия"
    teachers: list[PersonRef]
    groups: list[PersonRef]
    room: RoomRef | None


class ScheduleResponse(BaseModel):
    lessons: list[Lesson]
    date_from: date
    date_to: date
