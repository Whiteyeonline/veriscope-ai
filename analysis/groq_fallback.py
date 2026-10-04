"""
analysis/groq_fallback.py
Failover AI Engine leveraging Groq (LLaMA 3)
"""
import json
from typing import Dict, Any, Optional
from groq import Groq

class GroqEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.client = Groq(api_key=api_key)

    async def generate_analysis(self, evidence: Dict[str, Any], prompt_template: str, language: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("Groq API Key missing")

        formatted_prompt = prompt_template.format(
            evidence_json=json.dumps(evidence, indent=2),
            language=language
        )

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": formatted_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
