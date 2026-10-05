"""
analysis/groq_fallback.py
Groq LLM Integration - Production-Ready Fallback
"""
import json
import asyncio
from typing import Dict, Any, Optional

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqEngine:
    """Production-grade Groq LLM for AI fallback."""
    
    MODEL = "mixtral-8x7b-32768"
    TIMEOUT = 60

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ""
        self.client = None
        
        if self.api_key and Groq is not None:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Groq: {str(e)}")

    async def generate_analysis(
        self,
        evidence: Dict[str, Any],
        prompt_template: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """Generate AI-powered audit insights using Groq.
        
        Args:
            evidence: Business data dict
            prompt_template: Prompt with {evidence_json} and {language} placeholders
            language: English or Malayalam
            
        Returns:
            Dict with gbp_score, executive_summary, findings, action_plan
            
        Raises:
            RuntimeError: If API call fails
        """
        if not self.api_key or self.client is None:
            raise RuntimeError("Groq API key not configured")

        try:
            evidence_json = json.dumps(evidence, indent=2)
            full_prompt = prompt_template.replace(
                "{evidence_json}", evidence_json
            ).replace("{language}", language)

            # Run in executor
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        messages=[{"role": "user", "content": full_prompt}],
                        model=self.MODEL,
                        temperature=0.5,
                        max_tokens=2000,
                    )
                ),
                timeout=self.TIMEOUT
            )
            
            content = response.choices[0].message.content if response.choices else ""
            if not content:
                raise ValueError("Empty response from Groq")
            
            # Parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try extracting from markdown code blocks
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    result = json.loads(content[start:end].strip())
                elif "```" in content:
                    start = content.find("```") + 3
                    end = content.find("```", start)
                    result = json.loads(content[start:end].strip())
                else:
                    raise
            
            # Validate required fields
            required_fields = ["gbp_score", "executive_summary", "findings", "action_plan"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except asyncio.TimeoutError:
            raise RuntimeError("Groq request timed out. Please try again.")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Groq returned invalid JSON: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")
