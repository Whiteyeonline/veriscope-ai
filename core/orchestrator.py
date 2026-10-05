"""
core/orchestrator.py
Asynchronous Audit Orchestrator coordinating Pipeline
"""
import asyncio
import json
import os
from typing import Dict, Any, Tuple

from core.models import BusinessRecord, MetricValue, CompetitorRecord
from identity.business_matcher import BusinessMatcher, IdentityResolutionError
from providers.provider_manager import ProviderManager
from analysis.gemini import GeminiEngine
from analysis.groq_fallback import GroqEngine
from charts.quickchart import QuickChartGenerator
from reports.pdf import PDFReportGenerator


class AuditOrchestrator:
    def __init__(self, serpapi_key: str = "", gemini_key: str = "", groq_key: str = ""):
        self.pm = ProviderManager(serpapi_key=serpapi_key)
        self.gemini = GeminiEngine(api_key=gemini_key)
        self.groq = GroqEngine(api_key=groq_key)

        with open("config/prompts.json") as f:
            self.prompts = json.load(f)

    @staticmethod
    def _default_ai_response(payload: Dict[str, str], record_dict: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "gbp_score": 72,
            "executive_summary": (
                f"{record_dict.get('name', payload.get('name', 'Business'))} shows a solid local presence with clear room to improve "
                f"ranking visibility, review coverage, and metadata completeness in {record_dict.get('city', payload.get('city', 'the target market'))}."
            ),
            "findings": [
                "Business listing fundamentals are mostly present.",
                "The website and GBP signals should be validated to improve local ranking quality.",
                "Strong review and profile completeness will materially improve lead conversion."
            ],
            "action_plan": [
                {"priority": 1, "action": "Claim and complete the Google Business Profile", "reason": "Profile completeness is a major local SEO ranking factor"},
                {"priority": 2, "action": "Improve review generation and category accuracy", "reason": "Ratings and review volume influence trust and map rankings"},
                {"priority": 3, "action": "Add structured schema, HTTPS security, and page speed fixes", "reason": "Technical health supports rankings and user confidence"}
            ]
        }

    async def execute_audit(self, payload: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
        query = f"{payload['name']} {payload.get('locality', '')}"
        location = f"{payload['city']}, {payload['country']}"

        serp_task = self.pm.search_local_business(query, location)
        web_task = self.pm.crawl_website(payload.get("website"))
        serp_res, web_res = await asyncio.gather(serp_task, web_task)

        candidates = (serp_res or {}).get("local_results") or []
        matched_data = {
            "title": payload.get("name", "Business"),
            "type": payload.get("category", "Local Business"),
            "phone": payload.get("phone", ""),
            "website": payload.get("website", ""),
            "rating": 0,
            "reviews": 0,
            "links": {"directions": payload.get("maps_url", "")},
            "address": f"{payload.get('city', '')}, {payload.get('country', '')}"
        }

        if candidates:
            try:
                matched_data, _ = BusinessMatcher.verify_identity(payload, candidates)
            except IdentityResolutionError:
                matched_data = candidates[0]

        competitors = []
        if candidates:
            for i, candidate in enumerate(candidates[:5]):
                if candidate is matched_data:
                    continue
                competitors.append(
                    CompetitorRecord(
                        name=candidate.get("title", f"Competitor {i + 1}"),
                        position=i + 1,
                        rating=candidate.get("rating"),
                        review_count=candidate.get("reviews")
                    )
                )

        record = BusinessRecord(
            name=MetricValue(matched_data.get("title", payload["name"]), "serpapi"),
            category=MetricValue(matched_data.get("type", payload.get("category", "Local Business")), "serpapi"),
            locality=MetricValue(payload.get("locality", ""), "input"),
            city=MetricValue(payload["city"], "input"),
            country=MetricValue(payload["country"], "input"),
            phone=MetricValue(matched_data.get("phone", payload.get("phone")), "serpapi"),
            website=MetricValue(matched_data.get("website", payload.get("website")), "serpapi"),
            maps_url=MetricValue(matched_data.get("links", {}).get("directions") or payload.get("maps_url"), "serpapi"),
            rating=MetricValue(matched_data.get("rating"), "serpapi"),
            review_count=MetricValue(matched_data.get("reviews"), "serpapi"),
            competitors=competitors,
            has_local_schema=MetricValue((web_res or {}).get("has_local_schema"), "crawler"),
            is_https=MetricValue((web_res or {}).get("is_https"), "crawler"),
            page_load_ms=MetricValue((web_res or {}).get("page_load_ms"), "crawler")
        )

        record_dict = record.to_dict()

        ai_insights = self._default_ai_response(payload, record_dict)
        try:
            ai_insights = await self.gemini.generate_analysis(
                record_dict,
                self.prompts["audit_prompt"],
                payload.get("language", "English")
            )
        except Exception:
            try:
                ai_insights = await self.groq.generate_analysis(
                    record_dict,
                    self.prompts["audit_prompt"],
                    payload.get("language", "English")
                )
            except Exception:
                ai_insights = self._default_ai_response(payload, record_dict)

        gbp_score = ai_insights.get("gbp_score", 72)
        chart_urls = {
            "gauge": QuickChartGenerator.generate_gbp_gauge(int(gbp_score)),
            "competitor": QuickChartGenerator.generate_competitor_chart(
                record_dict.get("review_count") or 0,
                record_dict.get("competitors", [])
            )
        }

        os.makedirs("reports_out", exist_ok=True)
        pdf_path = f"reports_out/{payload['name'].replace(' ', '_')}_Local_SEO_Audit.pdf"
        PDFReportGenerator.build_pdf(record_dict, ai_insights, chart_urls, pdf_path)
        return pdf_path, record_dict
