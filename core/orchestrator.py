"""
core/orchestrator.py
Asynchronous Audit Orchestrator coordinating the complete pipeline
"""
import asyncio
import json
import os
from typing import Any, Dict, Tuple

from analysis.gemini import GeminiEngine
from analysis.groq_fallback import GroqEngine
from charts.quickchart import QuickChartGenerator
from core.models import BusinessRecord, CompetitorRecord, MetricValue
from identity.business_matcher import BusinessMatcher, IdentityResolutionError
from providers.provider_manager import ProviderManager
from reports.pdf import PDFReportGenerator


class AuditOrchestrator:
    def __init__(self, serpapi_key: str = "", gemini_key: str = "", groq_key: str = ""):
        self.pm = ProviderManager(serpapi_key=serpapi_key)
        self.gemini = GeminiEngine(api_key=gemini_key)
        self.groq = GroqEngine(api_key=groq_key)
        self.serpapi_key = serpapi_key
        self.gemini_key = gemini_key
        self.groq_key = groq_key

        try:
            with open("config/prompts.json") as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            self.prompts = {
                "system_instruction": "You are a senior Local SEO analyst.",
                "audit_prompt": "Analyze this business data: {evidence_json}\n\nReturn JSON with gbp_score, executive_summary, findings, and action_plan in {language}.",
            }

    async def execute_audit(self, payload: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
        if not self.serpapi_key:
            raise RuntimeError("SERPAPI_API_KEY is required to generate accurate local SEO reports.")

        if not self.gemini_key and not self.groq_key:
            raise RuntimeError("At least one AI provider key is required: GEMINI_API_KEY or GROQ_API_KEY.")

        name = (payload.get("name") or "").strip()
        city = (payload.get("city") or "").strip()
        country = (payload.get("country") or "").strip()
        locality = (payload.get("locality") or "").strip()
        website = (payload.get("website") or "").strip()

        if not name or not city or not country:
            raise ValueError("Business name, city, and country are required.")

        query = name if not locality else f"{name} {locality}"
        location = f"{city}, {country}"

        print(f"\n🔍 Searching for: {query} in {location}")

        serp_task = self.pm.search_local_business(query, location)
        web_task = self.pm.crawl_website(website)
        serp_res, web_res = await asyncio.gather(serp_task, web_task)

        candidates = serp_res.get("local_results", [])
        if not candidates:
            raise RuntimeError(f"No local business results found for '{query}' in {location}.")

        try:
            matched_data, confidence = BusinessMatcher.verify_identity(payload, candidates)
            print(f"✓ Matched with {confidence * 100:.0f}% confidence")
        except IdentityResolutionError:
            matched_data = candidates[0]
            print("⚠ Using first result as fallback due to low-confidence identity match.")

        competitors = []
        for i, candidate in enumerate(candidates):
            if candidate == matched_data:
                continue
            if len(competitors) >= 3:
                break
            competitors.append(
                CompetitorRecord(
                    name=candidate.get("title") or candidate.get("name") or f"Competitor {i + 1}",
                    position=i + 1,
                    rating=candidate.get("rating"),
                    review_count=candidate.get("reviews") or candidate.get("review_count"),
                )
            )

        record = BusinessRecord(
            name=MetricValue(matched_data.get("title") or matched_data.get("name") or payload.get("name"), "serpapi"),
            category=MetricValue(matched_data.get("type") or payload.get("category", "Local Business"), "serpapi"),
            locality=MetricValue(locality, "input"),
            city=MetricValue(city, "input"),
            country=MetricValue(country, "input"),
            phone=MetricValue(matched_data.get("phone") or payload.get("phone"), "serpapi"),
            website=MetricValue(matched_data.get("website") or website, "serpapi"),
            maps_url=MetricValue(matched_data.get("maps_url") or matched_data.get("link") or payload.get("maps_url"), "serpapi"),
            rating=MetricValue(matched_data.get("rating"), "serpapi"),
            review_count=MetricValue(matched_data.get("reviews") or matched_data.get("review_count"), "serpapi"),
            competitors=competitors,
            has_local_schema=MetricValue((web_res or {}).get("has_local_schema"), "crawler"),
            is_https=MetricValue((web_res or {}).get("is_https"), "crawler"),
            page_load_ms=MetricValue((web_res or {}).get("page_load_ms"), "crawler"),
        )

        record_dict = record.to_dict()

        ai_insights = None
        if self.gemini_key:
            try:
                ai_insights = await self.gemini.generate_analysis(
                    record_dict,
                    self.prompts["audit_prompt"],
                    payload.get("language", "English"),
                )
                print("✓ Analysis powered by Google Gemini")
            except Exception as exc:
                print(f"⚠ Gemini failed: {exc}")

        if not ai_insights and self.groq_key:
            try:
                ai_insights = await self.groq.generate_analysis(
                    record_dict,
                    self.prompts["audit_prompt"],
                    payload.get("language", "English"),
                )
                print("✓ Analysis powered by Groq")
            except Exception as exc:
                print(f"⚠ Groq failed: {exc}")

        if not ai_insights:
            raise RuntimeError("Failed to generate AI analysis. Check your API keys and usage quotas.")

        gbp_score = ai_insights.get("gbp_score", 50)
        chart_urls = {
            "gauge": QuickChartGenerator.generate_gbp_gauge(int(gbp_score)),
            "competitor": QuickChartGenerator.generate_competitor_chart(
                record_dict.get("review_count") or 0,
                record_dict.get("competitors", []),
            ),
        }

        os.makedirs("reports_out", exist_ok=True)
        safe_name = name.replace(" ", "_").replace("/", "_")
        safe_city = city.replace(" ", "_").replace("/", "_")
        pdf_path = f"reports_out/{safe_name}_Local_SEO_Audit_{safe_city}.pdf"
        PDFReportGenerator.build_pdf(
            record_dict,
            ai_insights,
            chart_urls,
            pdf_path,
            language=payload.get("language", "English"),
        )
        return pdf_path, record_dict
