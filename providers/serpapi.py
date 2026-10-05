"""
providers/serpapi.py
SerpAPI Integration for Google Maps & Search Rankings
Production-ready with comprehensive error handling
"""
import aiohttp
import time
from typing import Dict, Any, Optional
from providers.base import BaseProvider


class SerpApiProvider(BaseProvider):
    """SerpAPI provider for live Google Maps search results."""
    
    BASE_URL = "https://serpapi.com/search"
    TIMEOUT = 30
    RETRIES = 2

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="serpapi", requires_key=True, priority=1)
        self.api_key = api_key

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """Fetch local business results from Google Maps via SerpAPI.
        
        Args:
            query: Business name + location search query
            location: City, Country format
            engine: google_maps or google (default: google_maps)
            
        Returns:
            Dict with 'local_results' array containing:
                - title: Business name
                - rating: Google rating (0-5)
                - reviews: Number of reviews
                - type: Business category
                - address: Full address
                - phone: Phone number
                - website: Business website
                - maps_url/link: Google Maps listing URL
        """
        if not self.api_key:
            raise RuntimeError("SerpAPI key is required")
        
        query = kwargs.get("query", "")
        location = kwargs.get("location", "")
        engine = kwargs.get("engine", "google_maps")

        if not query or not location:
            raise ValueError("query and location are required")

        params = {
            "engine": engine,
            "q": query,
            "location": location,
            "api_key": self.api_key
        }

        # Retry logic for transient failures
        for attempt in range(self.RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.BASE_URL,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            # Parse and normalize response
                            return {
                                "local_results": self._parse_results(data.get("local_results", [])),
                                "search_parameters": data.get("search_parameters", {}),
                                "search_metadata": data.get("search_metadata", {})
                            }
                        
                        elif resp.status == 402:
                            raise RuntimeError(
                                "SerpAPI quota exceeded. Please upgrade your plan at https://serpapi.com"
                            )
                        elif resp.status == 403:
                            raise RuntimeError(
                                "SerpAPI key is invalid. Please check your credentials at https://serpapi.com"
                            )
                        elif resp.status == 429:
                            # Rate limited - retry after delay
                            if attempt < self.RETRIES - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise RuntimeError("SerpAPI rate limit exceeded. Please try again later.")
                        else:
                            raise RuntimeError(f"SerpAPI returned HTTP {resp.status}")
            
            except asyncio.TimeoutError:
                if attempt < self.RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                raise RuntimeError("SerpAPI request timeout. Please try again.")
            except aiohttp.ClientError as e:
                if attempt < self.RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                raise RuntimeError(f"Network error connecting to SerpAPI: {str(e)}")
        
        raise RuntimeError("Failed to fetch from SerpAPI after retries")

    @staticmethod
    def _parse_results(results: list) -> list:
        """Parse and normalize SerpAPI results."""
        normalized = []
        for item in results:
            normalized.append({
                "title": item.get("title", ""),
                "rating": item.get("rating"),
                "reviews": item.get("review_count") or item.get("reviews"),
                "type": item.get("type", ""),
                "address": item.get("address", ""),
                "phone": item.get("phone", ""),
                "website": item.get("website", ""),
                "maps_url": item.get("maps_url"),
                "link": item.get("link"),
                "review_count": item.get("review_count") or item.get("reviews"),
                "review_highlights": item.get("review_highlights", []),
                "review_snippets": item.get("review_snippets", []),
                "photos": item.get("photos", []),
                "links": item.get("links", {})
            })
        return normalized


import asyncio
