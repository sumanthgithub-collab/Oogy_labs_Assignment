import logging
from typing import Dict, Any, Optional
from app.providers.base import LLMProvider
from app.config import settings
import openai

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name or settings.OPENAI_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY environment variable.")

        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI provider failed: {str(e)}")

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model_name": self.model_name,
            "status": "active" if self.api_key else "missing_key"
        }
