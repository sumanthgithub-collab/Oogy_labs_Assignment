import logging
from typing import Dict, Any, Optional
from app.providers.base import LLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.mock_provider import MockLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)

class LLMProviderRouter:
    def __init__(self):
        self._active_provider_name: str = settings.LLM_PROVIDER
        self._custom_model: Optional[str] = None
        self._provider_instances: Dict[str, LLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        self._provider_instances = {
            "ollama": OllamaProvider(model_name=self._custom_model or settings.OLLAMA_MODEL),
            "anthropic": AnthropicProvider(model_name=self._custom_model or settings.ANTHROPIC_MODEL),
            "openai": OpenAIProvider(model_name=self._custom_model or settings.OPENAI_MODEL),
            "mock": MockLLMProvider()
        }

    def get_active_provider(self) -> LLMProvider:
        provider_name = self._active_provider_name.lower()
        if provider_name in self._provider_instances:
            return self._provider_instances[provider_name]
        logger.warning(f"Unknown provider '{provider_name}'. Falling back to mock provider.")
        return self._provider_instances["mock"]

    def set_provider(self, provider_name: str, model_name: Optional[str] = None) -> Dict[str, Any]:
        p_name = provider_name.lower()
        if p_name not in ["ollama", "anthropic", "openai", "mock"]:
            raise ValueError(f"Invalid provider: '{provider_name}'. Supported: ollama, anthropic, openai, mock")

        self._active_provider_name = p_name
        if model_name:
            self._custom_model = model_name

        self._init_providers()
        logger.info(f"Switched LLM provider to: {self._active_provider_name} (model: {model_name or 'default'})")
        return self.get_config()

    def get_config(self) -> Dict[str, Any]:
        active_instance = self.get_active_provider()
        info = active_instance.get_info()
        return {
            "provider": self._active_provider_name,
            "model_name": info.get("model_name", "unknown"),
            "status": info.get("status", "active"),
            "available_providers": ["ollama", "anthropic", "openai", "mock"]
        }

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        active_provider = self.get_active_provider()
        try:
            return await active_provider.generate(prompt=prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"Active provider '{self._active_provider_name}' failed: {e}. Attempting fallback to mock provider.")
            fallback = self._provider_instances["mock"]
            return await fallback.generate(prompt=prompt, system_prompt=system_prompt)

provider_router = LLMProviderRouter()
