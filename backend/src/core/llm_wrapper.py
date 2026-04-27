"""
LLM Wrapper
Wrapper unificado para Ollama e Gemini API
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMWrapper:
    """Wrapper unificado para diferentes provedores de LLM"""

    def __init__(self, provider: str = "ollama", api_key: Optional[str] = None):
        """
        Args:
            provider: "ollama" ou "gemini"
            api_key: Chave da API (necessária para Gemini)
        """
        self.provider = provider
        self._client = None
        self._api_key = api_key

    def _get_client(self):
        """Lazy initialization do cliente"""
        if self._client is not None:
            return self._client

        if self.provider == "ollama":
            from .ollama_client import OllamaClient
            self._client = OllamaClient()
        elif self.provider == "gemini":
            from .gemini_client import GeminiClient
            self._client = GeminiClient(api_key=self._api_key)
        else:
            raise ValueError(f"Provider desconhecido: {self.provider}")

        return self._client

    def is_available(self) -> bool:
        """Verifica se o LLM está disponível"""
        try:
            client = self._get_client()
            return client.is_available()
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade do LLM: {e}")
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Gera texto usando o LLM configurado"""
        client = self._get_client()
        return client.generate(prompt, system_prompt)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Gera JSON estruturado usando o LLM configurado"""
        client = self._get_client()
        return client.generate_json(prompt, system_prompt)

    def close(self):
        """Fecha o cliente"""
        if self._client:
            self._client.close()
