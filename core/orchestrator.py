"""
core/orchestrator.py
Asynchronous Audit Orchestrator coordinating the complete pipeline
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
        self.serpapi_key = serpapi_key
        self.gemini_key = gemini_key
        self.groq_key = groq_key

        # Load prompts
        try:
            with open("config/prompts.json") as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            # Fallback prompts if file not found
            self.prompts = {
                "system_instruction": "You are a senior Local SEO analyst.",
                "audit_prompt": "Analyze this business data: {evidence_json}\n\nReturn JSON with gbp_score, executive_summary, findings, and action_plan in {language}."
            }

    async def execute_audit(self, payload: Dict[str, str]) -> Tuple[str, Dict[str, Any]]:
        """Execute the complete audit pipeline.
        
        Args:
            payload: Business input dict with name, city, country, website, etc.
            
        Returns:
            (pdf_path, record_dict)
            
        Raises:
            RuntimeError: If SERPAPI_API_KEY is missing (required for live data)
        """
        
        # Validate required APIs
        if not self.serpapi_key:
            raise RuntimeError(
                "SERPAPI_API_KEY is required to generate accurate local SEO reports. "
                "Please set your API key in environment variables or .env file. "
                "Get a free key at https://serpapi.com"
            )
        
        if not self.gemini_key and not self.groq_key:
            raise RuntimeError(
                "At least one AI provider key (GEMINI_API_KEY or GROQ_API_KEY) is required. "
                "Get free keys at https://ai.google.dev or https://console.groq.com"
            )
        
        # Step 1: Parallel Harvesting (SERP & Website Crawl)
        query = f"{payload['name']} {payload.get('locality', '')}"
        location = f"{payload['city']}, {payload['country']}"

        print(f"\n🔍 Searching for: {query} in {location}")
        
        serp_task = self.pm.search_local_business(query, location)
        web_task = self.pm.crawl_website(payload.get("website"))
        
        serp_res, web_res = await asyncio.gather(serp_task, web_task)

        # Step 2: Identity Resolution
        candidates = serp_res.get("local_results", [])
        
        if not candidates:
            raise RuntimeError(
                f"No local business results found for '{query}' in {location}. "
                "Please verify the business name and location are correct."
            )
        
        print(f"Found {len(candidates)} local results. Matching to target business...")
        
        try:
            matched_data, confidence = BusinessMatcher.verify_identity(payload, candidates)
            print(f"✓ Matched with {confidence*100:.0f}% confidence")
        except IdentityResolutionError as e:
            raise RuntimeError(f"Could not verify business: {str(e)}")

        # Extract Competitors (top 3)
        competitors = []
        for i, candidate in enumerate(candidates):
            if candidate == matched_data:
                continue
            if len(competitors) >= 3:
                break
            competitors.append(
                CompetitorRecord(
                    name=candidate.get("title", f"Competitor {i+1}"),
                    position=i + 1,
                    rating=candidate.get("rating"),
                    review_count=candidate.get("reviews")
                )
            )

        # Normalize into BusinessRecord
        record = BusinessRecord(
            name=MetricValue(matched_data.get("title", payload["name"]), "serpapi"),
            category=MetricValue(matched_data.get("type", payload.get("category", "Local Business")), "serpapi"),
            locality=MetricValue(payload.get("locality", ""), "input"),
            city=MetricValue(payload["city"], "input"),
            country=MetricValue(payload["country"], "input"),
            phone=MetricValue(matched_data.get("phone", payload.get("phone")), "serpapi"),
            website=MetricValue(matched_data.get("website", payload.get("website")), "serpapi"),
            maps_url=MetricValue(
                matched_data.get("maps_url") or matched_data.get("link") or payload.get("maps_url"),
                "serpapi"
            ),
            rating=MetricValue(matched_data.get("rating"), "serpapi"),
            review_count=MetricValue(matched_data.get("reviews"), "serpapi"),
            competitors=competitors,
            has_local_schema=MetricValue(web_res.get("has_local_schema") if web_res else False, "crawler"),
            is_https=MetricValue(web_res.get("is_https") if web_res else False, "crawler"),
            page_load_ms=MetricValue(web_res.get("page_load_ms") if web_res else None, "crawler")
        )

        record_dict = record.to_dict()
        print(f"✓ Business verified: {record_dict['name']} ({record_dict['review_count']} reviews, {record_dict['rating']} rating)")

        # Step 3: Evidence-First AI Analysis with Failover
        print("🤖 Generating AI-powered insights...")
        ai_insights = None
        
        if self.gemini_key:
            try:
                ai_insights = await self.gemini.generate_analysis(
                    record_dict,
                    self.prompts["audit_prompt"],
                    payload.get("language", "English")
                )
                print("✓ Analysis powered by Google Gemini")
            except Exception as e:
                print(f"⚠ Gemini failed: {e}. Trying Groq...")
        
        if not ai_insights and self.groq_key:
            try:
                ai_insights = await self.groq.generate_analysis(
                    record_dict,
                    self.prompts["audit_prompt"],
                    payload.get("language", "English")
                )
                print("✓ Analysis powered by Groq")
            except Exception as e:
                print(f"⚠ Groq failed: {e}")
        
        if not ai_insights:
            raise RuntimeError(
                "Failed to generate AI analysis. Check your API keys and quotas."
            )

        # Step 4: Generate Charts
        print("📊 Generating performance charts...")
        gbp_score = ai_insights.get("gbp_score", 50)
        chart_urls = {
            "gauge": QuickChartGenerator.generate_gbp_gauge(int(gbp_score)),
            "competitor": QuickChartGenerator.generate_competitor_chart(
                record_dict.get("review_count") or 0,
                record_dict.get("competitors", [])
            )
        }

        # Step 5: PDF Generation
        print("📄 Building executive PDF report...")
        os.makedirs("reports_out", exist_ok=True)
        pdf_path = f"reports_out/{payload['name'].replace(' ', '_')}_Local_SEO_Audit_{payload['city'].replace(' ', '_')}.pdf"
        PDFReportGenerator.build_pdf(record_dict, ai_insights, chart_urls, pdf_path, language=payload.get("language", "English"))
        
        print(f"✓ Report generated: {pdf_path}")
        return pdf_path, record_dict
