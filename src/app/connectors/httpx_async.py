"""
Асинхронный HTTP коннектор на базе httpx.AsyncClient.
"""

import asyncio
import json
import logging
import time
from typing import Any

import httpx

from .base_connectors import AbstractAsyncConnector

logger = logging.getLogger("app.connector")


class HTTPXAsyncConnector(AbstractAsyncConnector[httpx.AsyncClient]):
    """
    Асинхронный коннектор с использованием httpx.AsyncClient.
    Retry с экспоненциальной задержкой, разделение 4xx/5xx.
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
        base_url: str | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(max_retries=max_retries, retry_delay=retry_delay)
        if hasattr(self, "_httpx_initialized"):
            return
        self._httpx_initialized = True
        self.timeout = timeout
        self.base_url = base_url
        self.default_headers = default_headers or {}
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            base_url=self.base_url,
            headers=self.default_headers,
            verify=True,
        )

    async def request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """
        Асинхронный HTTP запрос с retry логикой и детальным логированием.

        Retry при 5xx и сетевых ошибках.
        4xx — сразу raise без retry.
        Экспоненциальная задержка: retry_delay * (2 ** attempt).
        """
        last_exception: Exception | None = None

        full_url = f"{self.base_url}{url}" if self.base_url and not url.startswith("http") else url
        logger.info(f">>> REQUEST: {method} {full_url}")

        if "params" in kwargs:
            logger.info(f"    Query params: {kwargs['params']}")

        if "json" in kwargs:
            try:
                formatted_json = json.dumps(kwargs["json"], indent=2, ensure_ascii=False)
                logger.info(f"    Request Body:\n{formatted_json}")
            except Exception:
                logger.info(f"    Request Body: {kwargs['json']}")

        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, **kwargs)
                duration = (time.time() - start_time) * 1000

                logger.info(f"<<< RESPONSE: {response.status_code} | {duration:.2f}ms | {method} {full_url}")

                try:
                    response_data = response.json()
                    formatted_response = json.dumps(response_data, indent=2, ensure_ascii=False)
                    if len(formatted_response) > 1000:
                        formatted_response = formatted_response[:1000] + "...(truncated)"
                    logger.info(f"    Response Body:\n{formatted_response}")
                except Exception:
                    logger.info(f"    Response Body: {response.text[:500]}")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"<<< ERROR: {e.response.status_code} | {duration:.2f}ms | {method} {full_url}")
                logger.error(f"    Error response: {e.response.text[:500]}")

                if 400 <= e.response.status_code < 500:
                    raise
                last_exception = e

            except (httpx.RequestError, httpx.TimeoutException) as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"<<< CONNECTION ERROR: {type(e).__name__} | {duration:.2f}ms | {method} {full_url}")
                logger.error(f"    Error: {str(e)}")
                last_exception = e

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"<<< UNEXPECTED ERROR: {type(e).__name__} | {duration:.2f}ms | {method} {full_url}")
                logger.error(f"    Error: {str(e)}")
                last_exception = e

            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(f"    Retrying in {delay:.1f}s... (attempt {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(delay)

        raise last_exception or Exception("Request failed after all retries")

    async def shutdown(self) -> None:
        """Закрытие httpx.AsyncClient."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
