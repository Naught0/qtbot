from __future__ import annotations

from typing import Any, Generic, TypedDict, TypeVar

import aiohttp


class SearchMetadata(TypedDict):
    id: str
    status: str
    json_endpoint: str
    created_at: str
    processed_at: str
    raw_html_file: str
    total_time_taken: float


class SearchParameters(TypedDict, total=False):
    engine: str
    q: str
    location: str
    google_domain: str
    hl: str
    gl: str
    device: str


class SerpapiPagination(TypedDict, total=False):
    current: int
    next: str


SearchResultT = TypeVar("SearchResultT")


class SerpApiBase(Generic[SearchResultT]):
    """Base client for the serpapi.com search API.

    Subclasses set ``engine`` and parameterize the response TypedDict,
    e.g. ``class GoogleSearch(SerpApiBase[GoogleSearchResult])``.
    """

    base_url = "https://serpapi.com"
    engine: str

    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        self.session = session
        self.api_key = api_key

    async def _make_request(self, params: dict[str, Any]) -> SearchResultT:
        async with self.session.get(
            f"{self.base_url}/search.json",
            params={"api_key": self.api_key, "engine": self.engine, **params},
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def search(self, query: str, **kwargs: Any) -> SearchResultT:
        """Search for ``query``; kwargs are passed through as extra serpapi params."""
        return await self._make_request({"q": query[:256], **kwargs})
