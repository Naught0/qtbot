from __future__ import annotations

from typing import TypedDict

from lib.serpapi import SearchMetadata, SearchParameters, SerpApiBase, SerpapiPagination


class ImageSearchMetadata(SearchMetadata):
    google_images_light_url: str


class ImageSearchInformation(TypedDict):
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


class ImageSearchResult(TypedDict):
    search_metadata: ImageSearchMetadata
    search_parameters: SearchParameters
    search_information: ImageSearchInformation
    images_results: list[LightImageResult]
    serpapi_pagination: SerpapiPagination


class ImageSearch(SerpApiBase[ImageSearchResult]):
    engine = "google_images_light"
