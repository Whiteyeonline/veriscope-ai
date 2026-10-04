"""
providers/serpapi.py
SerpAPI Integration for Maps & Search Rankings
"""
import aiohttp
from typing import Dict, Any, Optional
from providers.base import BaseProvider

class SerpApiProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="serpapi", requires_key=True, priority=1)
        self.api_key = api_key

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            return {"error": "Missing SerpAPI Key"}
        
        query = kwargs.get("query", "")
        location = kwargs.get("location", "")
        engine = kwargs.get("engine", "google_maps")

        params = {
            "engine": engine,
            "q": query,
            "location": location,
            "api_key": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get("https://serpapi.com/search", params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"error": f"SerpAPI returned HTTP {resp.status}"}
