import logging
from typing import Dict, Any, Optional
from app.providers.base import LLMProvider
from app.config import settings
import anthropic

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model_name = model_name or settings.ANTHROPIC_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key is missing. Please set ANTHROPIC_API_KEY environment variable.")

        try:
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = await client.messages.create(**kwargs)
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise RuntimeError(f"Anthropic provider failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "anthropic",
            "model_name": self.model_name,
            "status": "active" if self.api_key else "missing_key"
        }
