"""
Коннектор к schedule-of.mirea.ru.
"""

from typing import Any

from .httpx_async import HTTPXAsyncConnector


class ScheduleConnector(HTTPXAsyncConnector):
    """Коннектор к schedule-of.mirea.ru."""

    BASE_URL = "https://schedule-of.mirea.ru"

    def __init__(self) -> None:
        super().__init__(base_url=self.BASE_URL, timeout=15.0)

    async def search(self, query: str, limit: int = 15) -> dict[str, Any]:
        """Поиск групп, преподавателей, кабинетов."""
        return await self.get("/schedule/api/search", params={"match": query, "limit": limit})

    async def get_ical(self, schedule_type: int, entity_id: int) -> str:
        """Возвращает сырой iCal текст."""
        response = await self._client.get(
            f"/schedule/api/ical/{schedule_type}/{entity_id}",
            params={"includeMeta": "true"},
        )
        response.raise_for_status()
        return response.text

    async def get_week_number(self) -> dict[str, Any]:
        """Возвращает номер текущей учебной недели."""
        return await self.get("/schedule/api/weeknumber/receiver/attendance_high_school")
