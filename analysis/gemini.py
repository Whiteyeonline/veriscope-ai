"""
analysis/gemini.py
Google Gemini AI Integration - Production-Ready
"""
import json
import asyncio
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiEngine:
    """Production-grade Gemini AI for business analysis."""
    
    MODEL = "gemini-2.0-flash"
    TIMEOUT = 60

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.model = None
        
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.MODEL)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Gemini: {str(e)}")

    async def generate_analysis(
        self,
        evidence: Dict[str, Any],
        prompt_template: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI-powered audit insights.
        
        Args:
            evidence: Business data dict from orchestrator
            prompt_template: Prompt with {evidence_json} and {language} placeholders
            language: English or Malayalam
            
        Returns:
            Dict with gbp_score, executive_summary, findings, action_plan
            
        Raises:
            RuntimeError: If API call fails
        """
        if not self.api_key or self.model is None:
            raise RuntimeError("Gemini API key not configured")

        try:
            evidence_json = json.dumps(evidence, indent=2)
            full_prompt = prompt_template.replace(
                "{evidence_json}", evidence_json
            ).replace("{language}", language)
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        full_prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                ),
                timeout=self.TIMEOUT
            )
            
            response_text = getattr(response, "text", "") or ""
            if not response_text:
                raise ValueError("Empty response from Gemini")
            
            # Parse JSON response
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["gbp_score", "executive_summary", "findings", "action_plan"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except asyncio.TimeoutError:
            raise RuntimeError("Gemini request timed out. Please try again.")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Gemini returned invalid JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
