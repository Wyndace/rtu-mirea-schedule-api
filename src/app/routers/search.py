"""
Роутер поиска групп/преподавателей/кабинетов.
"""

from typing import Annotated

from litestar import get
from litestar.params import Parameter

from app.connectors import ScheduleConnector
from app.schemas.search import ScheduleTarget, SearchResponse, SearchResultItem


@get("/api/search")
async def search(
    q: Annotated[str, Parameter(query="query", description="Поисковый запрос")],
    limit: int = 100,
) -> SearchResponse:
    """Поиск групп, преподавателей и кабинетов."""
    connector = ScheduleConnector()
    raw = await connector.search(query=q, limit=limit)

    items: list[SearchResultItem] = []
    for item in raw.get("data", []):
        try:
            target = ScheduleTarget(item["scheduleTarget"])
        except (ValueError, KeyError):
            continue
        items.append(
            SearchResultItem(
                id=item["id"],
                title=item["targetTitle"],
                full_title=item["fullTitle"],
                target=target,
            )
        )

    return SearchResponse(data=items)
