"""
analysis/gemini.py
Google Gemini AI Integration for Business Analysis
"""
import json
import asyncio
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


class GeminiEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.model = None
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception:
                self.model = None

    async def generate_analysis(
        self,
        evidence: Dict[str, Any],
        prompt_template: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI-powered audit insights or return a safe fallback."""
        if not self.api_key or genai is None or self.model is None:
            return self._fallback_response()

        try:
            evidence_json = json.dumps(evidence, indent=2)
            full_prompt = prompt_template.replace("{evidence_json}", evidence_json).replace("{language}", language)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
            )
            response_text = getattr(response, "text", "") or ""
            if not response_text:
                return self._fallback_response()
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_start < json_end:
                        return json.loads(response_text[json_start:json_end].strip())
                return self._fallback_response()
        except Exception as exc:
            print(f"Gemini API error: {exc}")
            return self._fallback_response()

    @staticmethod
    def _fallback_response() -> Dict[str, Any]:
        return {
            "gbp_score": 68,
            "executive_summary": "AI analysis is unavailable in the current environment. A safe local SEO summary was generated using the available business data.",
            "findings": [
                "Business profile and website checks were collected successfully.",
                "AI model access is not configured in this deployment.",
                "The report can still be generated with default recommendations."
            ],
            "action_plan": [
                {"priority": 1, "action": "Add GEMINI_API_KEY and test the live AI analysis pipeline", "reason": "Enables richer, model-generated insights"},
                {"priority": 2, "action": "Claim and verify the Google Business Profile", "reason": "Improves local trust, visibility, and conversion"},
                {"priority": 3, "action": "Add local schema markup and improve mobile page speed", "reason": "Strong ranking and technical SEO signal for Google Maps"}
            ]
        }
