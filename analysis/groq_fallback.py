"""
analysis/groq_fallback.py
Groq LLM for High-Speed Inference Fallback
"""
import json
import asyncio
from typing import Dict, Any, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.client = None
        if self.api_key and Groq is not None:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Groq init error: {e}")
                self.client = None

    async def generate_analysis(
        self,
        evidence: Dict[str, Any],
        prompt_template: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI-powered audit insights using Groq."""
        if not self.api_key or self.client is None:
            raise RuntimeError("Groq API key not configured")

        try:
            evidence_json = json.dumps(evidence, indent=2)
            full_prompt = prompt_template.replace("{evidence_json}", evidence_json).replace("{language}", language)

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    messages=[{"role": "user", "content": full_prompt}],
                    model="mixtral-8x7b-32768",
                    temperature=0.5,
                    max_tokens=2000,
                )
            )
            
            content = response.choices[0].message.content if response.choices else ""
            if not content:
                raise ValueError("Empty response from Groq")
            
            # Try to parse JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try extracting JSON from markdown code blocks
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    result = json.loads(content[json_start:json_end].strip())
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    result = json.loads(content[json_start:json_end].strip())
                else:
                    raise
            
            return result
            
        except Exception as e:
            print(f"Groq analysis error: {e}")
            raise
