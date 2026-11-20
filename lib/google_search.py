from __future__ import annotations

from typing import Any, TypedDict

import aiohttp

from lib.serpapi import SearchParameters, SerpApiBase, SerpapiPagination


class OrganicResult(TypedDict, total=False):
    position: int
    title: str
    link: str
    displayed_link: str
    snippet: str


class RelatedSearch(TypedDict):
    query: str
    link: str


class GoogleSearchInformation(TypedDict, total=False):
    query_displayed: str
    organic_results_state: str
    result_links: int
    time_taken_string: str


class GoogleSearchResult(TypedDict, total=False):
    search_parameters: SearchParameters
    search_information: GoogleSearchInformation
    organic_results: list[OrganicResult]
    related_searches: list[RelatedSearch]
    serpapi_pagination: SerpapiPagination


class GoogleSearch(SerpApiBase[GoogleSearchResult]):
    """google_light engine: lightweight HTML Google results as JSON."""

    engine = "google_light"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str,
        *,
        location: str | None = None,
        google_domain: str = "google.com",
        hl: str = "en",
        gl: str = "us",
    ):
        super().__init__(session, api_key)
        self.location = location
        self.google_domain = google_domain
        self.hl = hl
        self.gl = gl

    async def search(self, query: str, **kwargs: Any) -> GoogleSearchResult:
        params: dict[str, Any] = {
            "location": self.location,
            "google_domain": self.google_domain,
            "hl": self.hl,
            "gl": self.gl,
            **kwargs,
        }
        return await super().search(
            query, **{k: v for k, v in params.items() if v is not None}
        )
