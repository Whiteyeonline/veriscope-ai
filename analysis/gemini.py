"""
analysis/gemini.py
Primary AI Engine leveraging Google Gemini
"""
import json
import google.generativeai as genai
from typing import Dict, Any, Optional

class GeminiEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)

    async def generate_analysis(self, evidence: Dict[str, Any], prompt_template: str, language: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("Gemini API Key missing")

        model = genai.GenerativeModel("gemini-2.5-flash")
        formatted_prompt = prompt_template.format(
            evidence_json=json.dumps(evidence, indent=2),
            language=language
        )

        response = model.generate_content(
            formatted_prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        return json.loads(response.text)
