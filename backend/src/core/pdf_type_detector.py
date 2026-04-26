"""
PDF Type Detector
Determina se um PDF é digital (texto selecionável) ou escaneado (imagem)
"""

import pypdf
from typing import Tuple
from enum import Enum


class PDFType(Enum):
    DIGITAL = "digital"
    SCANNED = "scanned"
    MIXED = "mixed"


class PDFTypeDetector:
    def __init__(self, min_text_threshold: int = 100):
        """
        Args:
            min_text_threshold: Mínimo de caracteres para considerar PDF digital
        """
        self.min_text_threshold = min_text_threshold

    def detect(self, pdf_path: str) -> Tuple[PDFType, str]:
        """
        Detecta o tipo de PDF e retorna o tipo + texto extraído (se digital)
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Tuple[PDFType, str]: Tipo de PDF e texto extraído
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Extrai texto de todas as páginas
                text = ""
                total_pages = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                
                # Verifica quantidade de texto
                text_length = len(text.strip())
                
                # Se tiver pouco texto, provavelmente é escaneado
                if text_length < self.min_text_threshold:
                    return PDFType.SCANNED, ""
                
                # Se tiver texto suficiente, verifica se é texto útil
                # (não apenas caracteres aleatórios de OCR ruim)
                useful_chars = sum(1 for c in text if c.isalnum() or c.isspace())
                useful_ratio = useful_chars / text_length if text_length > 0 else 0
                
                if useful_ratio < 0.5:
                    return PDFType.SCANNED, ""
                
                return PDFType.DIGITAL, text
                
        except Exception as e:
            # Em caso de erro, assume escaneado (OCR vai tentar recuperar)
            return PDFType.SCANNED, ""
