"""
Парсер iCal расписания в список занятий.
"""

from datetime import date, datetime

from icalendar import Calendar
import recurring_ical_events

from app.schemas.schedule import Lesson, PersonRef, RoomRef


class ICalParser:
    """Парсер iCal в список занятий."""

    def parse(self, ical_text: str, date_from: date, date_to: date) -> list[Lesson]:
        cal = Calendar.from_ical(ical_text)
        events = recurring_ical_events.of(cal).between(date_from, date_to)
        lessons = []
        for event in events:
            if event.name != "VEVENT":
                continue
            # Пропускаем маркеры недель (all-day события без времени)
            dtstart = event.get("DTSTART")
            if dtstart is None:
                continue
            if isinstance(dtstart.dt, date) and not isinstance(dtstart.dt, datetime):
                continue
            lesson = self._parse_event(event)
            if lesson is not None:
                lessons.append(lesson)
        return sorted(lessons, key=lambda l: (l.date, l.time_start))

    def _get_all(self, event, prop_name: str) -> list:
        """Получить все значения многозначного свойства."""
        val = event.get(prop_name)
        if val is None:
            return []
        if isinstance(val, list):
            return val
        return [val]

    def _parse_event(self, event) -> Lesson | None:
        dtstart = event.get("DTSTART")
        dtend = event.get("DTEND")
        if dtstart is None or dtend is None:
            return None

        dt_start = dtstart.dt
        dt_end = dtend.dt
        if not isinstance(dt_start, datetime) or not isinstance(dt_end, datetime):
            return None

        teachers: list[PersonRef] = []
        for t in self._get_all(event, "X-META-TEACHER"):
            try:
                teacher_id = int(t.params.get("ID", 0))
            except (ValueError, AttributeError):
                teacher_id = 0
            teachers.append(PersonRef(id=teacher_id, name=str(t)))

        groups: list[PersonRef] = []
        for g in self._get_all(event, "X-META-GROUP"):
            try:
                group_id = int(g.params.get("ID", 0))
            except (ValueError, AttributeError):
                group_id = 0
            groups.append(PersonRef(id=group_id, name=str(g)))

        room: RoomRef | None = None
        auditorium = event.get("X-META-AUDITORIUM")
        if auditorium is not None:
            try:
                room_id = int(auditorium.params.get("ID", 0))
            except (ValueError, AttributeError):
                room_id = 0
            number = str(auditorium.params.get("NUMBER", str(auditorium)))
            campus = str(auditorium.params.get("CAMPUS", ""))
            room = RoomRef(id=room_id, number=number, campus=campus)

        discipline_prop = event.get("X-META-DISCIPLINE")
        lesson_type_prop = event.get("X-META-LESSON_TYPE")
        lesson_type_full_prop = event.get("X-META-FULL_LESSON_TYPE")

        return Lesson(
            date=dt_start.date(),
            time_start=dt_start.strftime("%H:%M"),
            time_end=dt_end.strftime("%H:%M"),
            discipline=str(discipline_prop) if discipline_prop is not None else "",
            lesson_type=str(lesson_type_prop) if lesson_type_prop is not None else "",
            lesson_type_full=str(lesson_type_full_prop) if lesson_type_full_prop is not None else "",
            teachers=teachers,
            groups=groups,
            room=room,
        )
