from __future__ import annotations

from typing import TypedDict

import aiohttp


class ImageSearch:
    base_url = "https://serpapi.com"

    def __init__(self, session: aiohttp.ClientSession, engine="google_images_light"):
        self.session = session
        self.engine = engine

    async def _make_request(self, query: str):
        resp = await self.session.get(
            f"{self.base_url}/search", params={"engine": self.engine, "q": query[:256]}
        )
        return resp

    async def search(self, query: str) -> SearchResult:
        resp = await self._make_request(query)
        resp.raise_for_status()

        data = await resp.json()
        return data


class SearchResult(TypedDict):
    search_metadata: SearchMetadata
    search_parameters: SearchParameters
    search_information: SearchInformation
    images_results: list[LightImageResult]
    serpapi_pagination: SerpapiPagination


class SearchMetadata(TypedDict):
    id: str
    status: str
    json_endpoint: str
    created_at: str
    processed_at: str
    google_images_light_url: str
    raw_html_file: str
    total_time_taken: float


class SearchParameters(TypedDict):
    engine: str
    q: str
    google_domain: str
    hl: str
    gl: str
    device: str


class SearchInformation(TypedDict):
    image_results_state: str


class LightImageResult(TypedDict):
    position: int
    title: str
    source: str
    link: str
    raw_link: str
    original: str
    original_width: int
    original_height: int
    thumbnail: str
    serpapi_thumbnail: str
    related_content_id: str
    serpapi_related_content_link: str


class SerpapiPagination(TypedDict):
    current: int
    next: str
