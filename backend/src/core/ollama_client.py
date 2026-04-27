"""
Ollama Client Wrapper
Interface para comunicação com Ollama API local
"""

import httpx
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", model: str = "qwen2.5:0.5b"):
        """
        Args:
            base_url: URL da API Ollama
            model: Modelo a ser usado (qwen2.5:0.5b é melhor para português e JSON)
        """
        self.base_url = base_url
        self.model = model
        self.client = httpx.Client(timeout=60.0)
        self._available = None

    def is_available(self) -> bool:
        """
        Verifica se Ollama está disponível
        """
        if self._available is not None:
            return self._available
        
        try:
            response = self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            self._available = response.status_code == 200
            return self._available
        except Exception as e:
            logger.warning(f"Ollama não disponível: {e}")
            self._available = False
            return False

    def model_exists(self) -> bool:
        """
        Verifica se o modelo específico existe no Ollama
        """
        try:
            response = self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                return self.model in model_names
            return False
        except Exception as e:
            logger.warning(f"Erro ao verificar modelo: {e}")
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Gera texto usando o modelo

        Args:
            prompt: Prompt do usuário
            system_prompt: System prompt opcional

        Returns:
            Texto gerado
        """
        if not self.is_available():
            raise RuntimeError("Ollama não está disponível")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_thread": 2,  # Força usar apenas 2 núcleos (otimizado para Celeron)
                "num_ctx": 2048,  # Limita janela de contexto para não travar a RAM
                "num_predict": 100,  # Limita tokens gerados
                "temperature": 0.1  # Mais determinístico
            }
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            print(f"[OLLAMA] Enviando requisição para {self.base_url}/api/generate")
            print(f"[OLLAMA] Payload: {payload}")
            response = self.client.post(f"{self.base_url}/api/generate", json=payload)
            print(f"[OLLAMA] Status code: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"[OLLAMA] Resposta recebida")
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Erro ao gerar com Ollama: {e}")
            print(f"[OLLAMA] ERRO: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera JSON estruturado usando o modelo
        
        Args:
            prompt: Prompt do usuário
            system_prompt: System prompt opcional
            
        Returns:
            Dicionário JSON
        """
        response_text = self.generate(prompt, system_prompt)
        
        try:
            # Tenta extrair JSON da resposta
            # Às vezes o LLM adiciona texto antes/depois do JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: tenta parsear a resposta inteira
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            logger.error(f"Resposta bruta: {response_text}")
            raise ValueError(f"Resposta não é JSON válido: {e}")

    def close(self):
        """Fecha o cliente HTTP"""
        self.client.close()
