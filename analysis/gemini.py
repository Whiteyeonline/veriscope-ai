"""
analysis/gemini.py
Google Gemini AI Integration for Business Analysis
"""
import json
import asyncio
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.model = None
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"Gemini init error: {e}")
                self.model = None

    async def generate_analysis(
        self,
        evidence: Dict[str, Any],
        prompt_template: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI-powered audit insights using Gemini."""
        if not self.api_key or genai is None or self.model is None:
            raise RuntimeError("Gemini API key not configured")

        try:
            evidence_json = json.dumps(evidence, indent=2)
            full_prompt = prompt_template.replace("{evidence_json}", evidence_json).replace("{language}", language)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
            )
            
            response_text = getattr(response, "text", "") or ""
            if not response_text:
                raise ValueError("Empty response from Gemini")
            
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            raise
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            raise
