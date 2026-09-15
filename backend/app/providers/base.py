from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates a text completion for the given prompt."""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Returns details about the provider and current model."""
        pass
