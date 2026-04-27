"""
Gemini API Client
Cliente para Google Gemini API como alternativa ao Ollama
"""

import os
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash-latest"):
        """
        Args:
            api_key: Chave da API Gemini (se None, busca da variável de ambiente GEMINI_API_KEY)
            model: Modelo Gemini (gemini-1.5-flash é rápido e barato)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.Client(timeout=30.0)
        self._available = None
        print(f"[GEMINI] Inicializado com modelo: {self.model}")
        print(f"[GEMINI] API Key (primeiros 10 chars): {self.api_key[:10] if self.api_key else 'None'}...")

    def is_available(self) -> bool:
        """Verifica se Gemini API está configurada"""
        if self._available is not None:
            return self._available

        if not self.api_key:
            logger.warning("GEMINI_API_KEY não configurada")
            self._available = False
            return False

        self._available = True
        return True

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Gera texto usando Gemini

        Args:
            prompt: Prompt do usuário
            system_prompt: System prompt opcional

        Returns:
            Texto gerado
        """
        if not self.is_available():
            raise RuntimeError("Gemini API não está configurada")

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 100,
                "candidateCount": 1
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        try:
            print(f"[GEMINI] Enviando requisição para {self.model}")
            print(f"[GEMINI] URL: {url}")
            print(f"[GEMINI] Payload: {payload}")
            response = self.client.post(url, json=payload)
            print(f"[GEMINI] Status code: {response.status_code}")
            print(f"[GEMINI] Response body: {response.text[:500]}")
            response.raise_for_status()
            result = response.json()

            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[GEMINI] Resposta recebida")
                return text
            else:
                logger.error("Resposta Gemini vazia")
                return ""

        except Exception as e:
            logger.error(f"Erro ao gerar com Gemini: {e}")
            print(f"[GEMINI] ERRO: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera JSON estruturado usando Gemini

        Args:
            prompt: Prompt do usuário
            system_prompt: System prompt opcional

        Returns:
            Dicionário JSON
        """
        # Adiciona instrução para retornar JSON
        json_prompt = f"{prompt}\n\nResponda APENAS com JSON válido, sem texto adicional."

        response_text = self.generate(json_prompt, system_prompt)

        try:
            import json
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON do Gemini: {e}")
            logger.error(f"Resposta: {response_text}")
            raise

    def close(self):
        """Fecha o cliente HTTP"""
        self.client.close()
