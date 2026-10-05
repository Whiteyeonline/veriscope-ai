"""
providers/serpapi.py
SerpAPI Integration for Google Maps & Search Rankings
Production-ready with graceful error handling.
"""
import asyncio
import aiohttp
from typing import Any, Dict, Optional

from providers.base import BaseProvider


class SerpApiProvider(BaseProvider):
    BASE_URL = "https://serpapi.com/search"
    TIMEOUT = 30

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="serpapi", requires_key=True, priority=1)
        self.api_key = api_key

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("SerpAPI key is required")

        query = (kwargs.get("query") or "").strip()
        location = (kwargs.get("location") or "").strip()
        engine = (kwargs.get("engine") or "google_maps").strip()

        if not query:
            raise ValueError("Query cannot be empty")
        if not location:
            raise ValueError("Location cannot be empty")

        params = {
            "engine": engine,
            "q": query,
            "location": location,
            "api_key": self.api_key,
        }

        print(f"[SerpAPI] Request -> q={query!r}, location={location!r}, engine={engine!r}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
                ) as resp:
                    text = await resp.text()
                    print(f"[SerpAPI] HTTP {resp.status}")
                    try:
                        data = await resp.json()
                    except Exception:
                        raise RuntimeError(f"SerpAPI returned non-JSON response: {text[:500]}")

                    if resp.status == 200:
                        results = data.get("local_results", [])
                        return {
                            "local_results": self._parse_results(results),
                            "search_parameters": data.get("search_parameters", {}),
                            "search_metadata": data.get("search_metadata", {}),
                        }

                    if resp.status == 400:
                        msg = data.get("error") or "Bad request"
                        raise RuntimeError(
                            f"SerpAPI returned 400 Bad Request. "
                            f"Query='{query}' Location='{location}'. Error: {msg}"
                        )

                    if resp.status == 401:
                        raise RuntimeError("SerpAPI authentication failed (401). Check your key in Streamlit Secrets.")

                    if resp.status == 402:
                        raise RuntimeError("SerpAPI quota exhausted (402). Upgrade your plan or try again later.")

                    if resp.status == 403:
                        raise RuntimeError("SerpAPI access forbidden (403). Check the key or account status.")

                    raise RuntimeError(f"SerpAPI returned HTTP {resp.status}: {data.get('error', 'Unknown error')}")

        except asyncio.TimeoutError:
            raise RuntimeError("SerpAPI request timed out. Try again or check the connection.")
        except aiohttp.ClientError as exc:
            raise RuntimeError(f"SerpAPI network error: {exc}")

    @staticmethod
    def _parse_results(results: list) -> list:
        parsed = []
        for item in results:
            parsed.append(
                {
                    "title": item.get("title") or item.get("name") or "Unknown",
                    "rating": item.get("rating"),
                    "reviews": item.get("review_count") or item.get("reviews"),
                    "type": item.get("type") or "",
                    "address": item.get("address") or "",
                    "phone": item.get("phone") or "",
                    "website": item.get("website") or "",
                    "maps_url": item.get("maps_url") or item.get("link"),
                    "link": item.get("link") or item.get("maps_url"),
                    "review_count": item.get("review_count") or item.get("reviews") or 0,
                    "review_highlights": item.get("review_highlights") or [],
                    "photos": item.get("photos") or [],
                }
            )
        return parsed
