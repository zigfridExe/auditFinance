"""
OCR Processor using PaddleOCR
Processa PDFs escaneados usando visão computacional
"""

import os
from paddleocr import PaddleOCR
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    def __init__(self, use_gpu: bool = False, lang: str = "pt"):
        """
        Args:
            use_gpu: Usar GPU para acelerar (False para CPU-only)
            lang: Idioma para OCR (pt = português)
        """
        self.use_gpu = use_gpu
        self.lang = lang
        self.ocr = None
        self._initialized = False

    def _initialize(self):
        """Inicializa o PaddleOCR (lazy loading)"""
        if self._initialized:
            return
        
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=self.lang,
                use_gpu=self.use_gpu,
                show_log=False
            )
            self._initialized = True
            logger.info("PaddleOCR inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar PaddleOCR: {e}")
            raise

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando OCR
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Texto extraído
        """
        self._initialize()
        
        try:
            result = self.ocr.ocr(image_path, cls=True)
            
            if not result or not result[0]:
                return ""
            
            # Concatena todo o texto reconhecido
            text_lines = []
            for line in result[0]:
                if line and len(line) > 0:
                    text_lines.append(line[1][0])  # line[1][0] é o texto
            
            return "\n".join(text_lines)
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto de {image_path}: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Converte PDF para imagens e extrai texto via OCR
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Texto extraído de todas as páginas
        """
        import fitz  # PyMuPDF
        
        self._initialize()
        
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Converte página para imagem
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom para melhor qualidade
                temp_image_path = f"/tmp/temp_page_{page_num}.png"
                pix.save(temp_image_path)
                
                # Extrai texto via OCR
                page_text = self.extract_text_from_image(temp_image_path)
                all_text.append(page_text)
                
                # Limpa imagem temporária
                os.remove(temp_image_path)
            
            doc.close()
            return "\n\n".join(all_text)
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF {pdf_path}: {e}")
            return ""
