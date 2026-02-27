"""
Абстрактные коннекторы для HTTP запросов.
"""

from abc import ABC, abstractmethod
from typing import Any, Self, TypeVar, Generic

TClient = TypeVar("TClient")
TAsyncClient = TypeVar("TAsyncClient")


class AbstractConnector(ABC):
    """
    Базовый абстрактный коннектор.
    Паттерн Singleton.
    """
    _instance: Self | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @abstractmethod
    def shutdown(self) -> None:
        """Закрытие соединения и освобождение ресурсов."""
        raise NotImplementedError


class AbstractSyncConnector(AbstractConnector, Generic[TClient]):
    """
    Абстрактный синхронный HTTP коннектор.
    """
    _client: TClient | None = None

    @abstractmethod
    def request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """HTTP запрос с retry логикой."""
        raise NotImplementedError

    def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """GET запрос."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """POST запрос."""
        return self.request("POST", url, **kwargs)

    @property
    def client(self) -> TClient | None:
        """Возвращает HTTP клиент."""
        return self._client


class AbstractAsyncConnector(AbstractConnector, Generic[TAsyncClient]):
    """
    Абстрактный асинхронный HTTP коннектор.
    """
    _client: TAsyncClient | None = None

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """Асинхронный HTTP запрос с retry логикой."""
        raise NotImplementedError

    async def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Асинхронный GET запрос."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Асинхронный POST запрос."""
        return await self.request("POST", url, **kwargs)

    @property
    def client(self) -> TAsyncClient | None:
        """Возвращает асинхронный HTTP клиент."""
        return self._client
