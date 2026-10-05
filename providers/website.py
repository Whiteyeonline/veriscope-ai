"""
providers/website.py
Direct HTTP Website Crawler with Schema & Performance Detection
Handles missing or invalid website URLs gracefully
"""
import time
import aiohttp
import asyncio
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Dict, Any
from providers.base import BaseProvider


class WebsiteCrawlerProvider(BaseProvider):
    """Crawls website for technical SEO metrics and schema detection."""
    
    TIMEOUT = 15
    MAX_SIZE = 5 * 1024 * 1024  # 5MB max

    def __init__(self):
        super().__init__(name="direct_crawler", requires_key=False, priority=1)

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """Crawl website and extract SEO metrics."""
        url = kwargs.get("url")
        if not url or not str(url).strip():
            return {
                "available": False,
                "reason": "No website URL provided",
                "is_https": False,
                "has_local_schema": False,
                "page_load_ms": 0,
                "status_code": 0
            }

        url = str(url).strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        start_time = time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache"
        }

        try:
            connector = aiohttp.TCPConnector(ssl=False, force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.get(
                        url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.TIMEOUT),
                        allow_redirects=True,
                        ssl=False
                    ) as resp:
                        page_load_ms = int((time.time() - start_time) * 1000)
                        final_url = str(resp.url)
                        is_https = final_url.startswith("https")
                        
                        if resp.status != 200:
                            return {
                                "available": False,
                                "status_code": resp.status,
                                "page_load_ms": page_load_ms,
                                "reason": f"HTTP {resp.status}",
                                "final_url": final_url,
                                "is_https": is_https,
                                "has_local_schema": False
                            }

                        content_length = resp.content_length or 0
                        if content_length > self.MAX_SIZE:
                            return {
                                "available": False,
                                "reason": "Page too large to analyze",
                                "page_load_ms": page_load_ms,
                                "final_url": final_url,
                                "is_https": is_https,
                                "has_local_schema": False
                            }

                        html = await resp.text(errors="ignore")
                        soup = BeautifulSoup(html, "html.parser")
                        metrics = self._extract_metrics(html, soup, final_url, page_load_ms, is_https)
                        metrics["status_code"] = resp.status
                        metrics["available"] = True
                        metrics["final_url"] = final_url
                        metrics["page_load_ms"] = page_load_ms
                        metrics["is_https"] = is_https
                        return metrics
                
                except asyncio.TimeoutError:
                    return {
                        "available": False,
                        "reason": "Request timeout",
                        "page_load_ms": int((time.time() - start_time) * 1000),
                        "timeout": True,
                        "is_https": False,
                        "has_local_schema": False
                    }
        
        except Exception as e:
            return {
                "available": False,
                "reason": str(e),
                "page_load_ms": int((time.time() - start_time) * 1000),
                "error_type": type(e).__name__,
                "is_https": False,
                "has_local_schema": False
            }

    @staticmethod
    def _extract_metrics(html: str, soup: BeautifulSoup, url: str, page_load_ms: int, is_https: bool) -> Dict[str, Any]:
        """Extract SEO and technical metrics from parsed HTML."""
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        meta_viewport = False
        for meta in soup.find_all("meta"):
            if meta.get("name") == "description":
                meta_desc = meta.get("content", "")
            if meta.get("name") == "viewport":
                meta_viewport = True

        # Canonical URL
        canonical = ""
        link_canonical = soup.find("link", {"rel": "canonical"})
        if link_canonical:
            canonical = link_canonical.get("href", "")

        # Schema detection
        has_local_schema = False
        schema_types = []
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                import json
                schema = json.loads(script.string or "{}")
                schema_type = schema.get("@type", "")
                schema_types.append(schema_type)
                if schema_type in ["LocalBusiness", "Organization", "Business", "Restaurant", "DoctorOffice", "Attorney", "HairSalon", "Store", "ProfessionalService"]:
                    has_local_schema = True
            except Exception:
                pass

        if "schema.org/LocalBusiness" in html or "schema.org/Organization" in html:
            has_local_schema = True

        h1_count = len(soup.find_all("h1"))
        h2_count = len(soup.find_all("h2"))
        images = soup.find_all("img")
        img_count = len(images)
        img_without_alt = sum(1 for img in images if not img.get("alt"))
        all_links = soup.find_all("a", href=True)
        internal_links = sum(1 for a in all_links if a["href"].startswith(("/", url)))
        external_links = sum(1 for a in all_links if a["href"].startswith(("http", "https")) and not a["href"].startswith(url))
        mobile_friendly = meta_viewport and "width=device-width" in html
        domain = urlparse(url).netloc.replace("www.", "")
        
        return {
            "title": title or "",
            "meta_description": meta_desc,
            "canonical_url": canonical,
            "has_local_schema": has_local_schema,
            "schema_types": schema_types,
            "mobile_friendly": mobile_friendly,
            "h1_count": h1_count,
            "h2_count": h2_count,
            "images_count": img_count,
            "images_without_alt": img_without_alt,
            "links_count": len(all_links),
            "internal_links": internal_links,
            "external_links": external_links,
            "domain": domain,
            "text_length": len(soup.get_text()),
            "headings_structure": h1_count > 0,
            "is_https": is_https,
            "page_load_ms": page_load_ms
        }
