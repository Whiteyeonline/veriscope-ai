"""
providers/website.py
Direct HTTP Crawler & Schema Detector with Performance Metrics
"""
import time
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any
from providers.base import BaseProvider


class WebsiteCrawlerProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="direct_crawler", requires_key=False, priority=1)

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url")
        if not url:
            return {"available": False, "reason": "No URL provided"}

        if not url.startswith("http"):
            url = "https://" + url

        start_time = time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as resp:
                    page_load_ms = int((time.time() - start_time) * 1000)
                    
                    if resp.status != 200:
                        return {
                            "available": False,
                            "status_code": resp.status,
                            "page_load_ms": page_load_ms
                        }

                    html = await resp.text()
                    soup = BeautifulSoup(html, "lxml")

                    # Check for local schema
                    has_schema = ("schema.org" in html.lower() or 
                                "ld+json" in html.lower() or
                                "LocalBusiness" in html or
                                "Organization" in html)

                    # Extract key metrics
                    title = soup.title.string if soup.title else ""
                    h1_count = len(soup.find_all("h1"))
                    meta_description = ""
                    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
                    if meta_desc_tag:
                        meta_description = meta_desc_tag.get("content", "")

                    return {
                        "available": True,
                        "is_https": url.startswith("https"),
                        "page_load_ms": page_load_ms,
                        "has_local_schema": has_schema,
                        "title": title or "",
                        "meta_description": meta_description,
                        "h1_count": h1_count,
                        "status_code": resp.status
                    }
        except asyncio.TimeoutError:
            return {"available": False, "reason": "Request timeout", "page_load_ms": int((time.time() - start_time) * 1000)}
        except Exception as e:
            return {"available": False, "reason": str(e), "page_load_ms": int((time.time() - start_time) * 1000)}


import asyncio
