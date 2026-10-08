"""Backend-only, provider-isolated web search for current public information."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WebSearchUnavailable(Exception):
    """Raised when current web information cannot be retrieved safely."""


class WebSearchService:
    """Normalizes a configured search provider without exposing its raw payload."""

    def __init__(self, *, enabled: bool | None = None, api_key: str | None = None, timeout: float | None = None, max_results: int | None = None):
        self.enabled = settings.WEB_SEARCH_ENABLED if enabled is None else enabled
        self.api_key = settings.WEB_SEARCH_API_KEY if api_key is None else api_key
        self.timeout = settings.WEB_SEARCH_TIMEOUT_SECONDS if timeout is None else timeout
        self.max_results = max(1, min(max_results or settings.WEB_SEARCH_MAX_RESULTS, 10))

    async def search(self, query: str) -> list[dict[str, str]]:
        query = query.strip()
        if not query:
            return []
        if not self.enabled:
            raise WebSearchUnavailable("Web search is disabled.")
        if settings.WEB_SEARCH_PROVIDER.lower() != "brave" or not self.api_key:
            raise WebSearchUnavailable("Web search is not configured.")
        return await self._search_brave(query)

    async def _search_brave(self, query: str) -> list[dict[str, str]]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    settings.WEB_SEARCH_BRAVE_URL,
                    params={"q": query, "count": self.max_results},
                    headers={"Accept": "application/json", "X-Subscription-Token": self.api_key},
                )
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
        except httpx.TimeoutException as exc:
            logger.warning("Web search timed out provider=brave")
            raise WebSearchUnavailable("Web search timed out.") from exc
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Web search failed provider=brave exception=%s", type(exc).__name__)
            raise WebSearchUnavailable("Web search is unavailable.") from exc

        raw_results = payload.get("web", {}).get("results", [])
        if not isinstance(raw_results, list):
            return []
        normalized: list[dict[str, str]] = []
        for item in raw_results[: self.max_results]:
            if not isinstance(item, dict):
                continue
            title, url, snippet = item.get("title"), item.get("url"), item.get("description")
            if isinstance(title, str) and isinstance(url, str) and isinstance(snippet, str):
                normalized.append({"title": title.strip(), "url": url.strip(), "snippet": snippet.strip()})
        return normalized
