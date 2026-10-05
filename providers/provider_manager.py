"""
providers/provider_manager.py
Orchestrates API calls, cache checks, and fallback logic
"""
from typing import Dict, Any, Optional

from core.cache import SQLiteCache
from providers.serpapi import SerpApiProvider
from providers.website import WebsiteCrawlerProvider


class ProviderManager:
    def __init__(self, serpapi_key: Optional[str] = None):
        self.cache = SQLiteCache()
        self.serpapi = SerpApiProvider(api_key=serpapi_key)
        self.crawler = WebsiteCrawlerProvider()

    async def search_local_business(self, query: str, location: str) -> Dict[str, Any]:
        cache_key = f"maps_search_{query}_{location}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        data = await self.serpapi.fetch_data(query=query, location=location, engine="google_maps")
        if "error" not in data:
            self.cache.set(cache_key, data)
        return data

    async def crawl_website(self, url: Optional[str]) -> Dict[str, Any]:
        if not url or not str(url).strip():
            return {
                "available": False,
                "reason": "No website URL provided",
                "is_https": False,
                "has_local_schema": False,
                "page_load_ms": 0,
                "status_code": 0,
            }

        cache_key = f"web_crawl_{url}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        data = await self.crawler.fetch_data(url=url)
        if data.get("available"):
            self.cache.set(cache_key, data)
        return data
