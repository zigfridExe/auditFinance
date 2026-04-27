"""
Semantic Structurer using Ollama (Qwen2.5-0.5B)
Estrutura texto bruto em JSON usando LLM local
"""

import json
import logging
from typing import Dict, Any, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class SemanticStructurer:
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Args:
            ollama_client: Instância do OllamaClient (se None, cria uma nova)
        """
        self.ollama = ollama_client or OllamaClient()
        self.system_prompt = """Você é um especialista em extrair dados financeiros de documentos de prestação de contas.

Sua tarefa é extrair informações estruturadas do texto fornecido e retornar um JSON válido.

Campos obrigatórios:
- data: Data do documento (formato DD/MM/YYYY ou null se não encontrar)
- valor: Valor total (número float ou null se não encontrar)
- descricao: Descrição resumida do documento
- categoria: Categoria do documento (ex: "Receita", "Despesa", "Manutenção", "Água", "Luz", "Internet", etc.)

Regras:
1. Retorne APENAS JSON válido, sem texto adicional
2. Se não encontrar um campo, use null
3. Valores devem ser números (ex: 1500.50, não "R$ 1.500,50")
4. Datas devem estar no formato DD/MM/YYYY
5. Seja conciso e preciso"""

    def structure(self, raw_text: str) -> Dict[str, Any]:
        """
        Estrutura texto bruto em JSON
        
        Args:
            raw_text: Texto bruto do documento
            
        Returns:
            Dicionário com dados estruturados
        """
        if not raw_text or len(raw_text.strip()) < 10:
            logger.warning("Texto muito curto para estruturação")
            return {
                "data": None,
                "valor": None,
                "descricao": "Texto insuficiente",
                "categoria": "Erro"
            }
        
        try:
            # Tenta usar Ollama para estruturação
            prompt = f"""Extraia os dados financeiros deste texto:

{raw_text}

Retorne o JSON com os campos: data, valor, descricao, categoria"""
            
            result = self.ollama.generate_json(prompt, self.system_prompt)
            
            # Valida campos obrigatórios
            if not isinstance(result, dict):
                raise ValueError("Resposta não é um dicionário")
            
            # Garante campos existem
            for field in ["data", "valor", "descricao", "categoria"]:
                if field not in result:
                    result[field] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao estruturar com Ollama: {e}")
            # Fallback: retorna estrutura vazia
            return {
                "data": None,
                "valor": None,
                "descricao": "Erro na estruturação",
                "categoria": "Erro"
            }

    def is_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        return self.ollama.is_available()
