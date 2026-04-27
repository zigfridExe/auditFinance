"""
OCR Processor using Paddle
Processador de OCR usando PaddleOCR com fallback para Tesseract
"""

import os
# from paddleocr import PaddleOCR  # PaddleOCR não está instalado
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    def __init__(self, lang: str = "pt"):
        """
        Args:
            lang: Idioma para OCR (pt = português)
        """
        self.lang = lang
        self.ocr = None
        self._initialized = False
        self._use_tesseract = False
        self._tesseract = None

    def _initialize(self):
        """Inicializa o OCR (usa Tesseract por padrão por ser mais compatível)"""
        if self._initialized:
            return

        # Usa Tesseract diretamente (mais compatível)
        print(f"[OCR] Usando Tesseract OCR...")
        self._use_tesseract = True

        try:
            from .tesseract_ocr import TesseractOCR
            self._tesseract = TesseractOCR(lang="por" if self.lang == "pt" else "eng")
            self._initialized = True
            print(f"[OCR] Tesseract inicializado com sucesso")
        except ImportError:
            logger.error("Tesseract não disponível")
            raise RuntimeError("Tesseract não está disponível")

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando OCR

        Args:
            image_path: Caminho da imagem

        Returns:
            Texto extraído
        """
        print(f"[OCR] Iniciando extração de {image_path}")
        self._initialize()
        print(f"[OCR] OCR inicializado")

        try:
            if self._use_tesseract:
                print(f"[OCR] Usando Tesseract...")
                return self._tesseract.extract_text_from_image(image_path)
            else:
                print(f"[OCR] Executando PaddleOCR na imagem...")
                result = self.ocr.ocr(image_path, cls=True)
                print(f"[OCR] OCR concluído")

                if not result or not result[0]:
                    print(f"[OCR] Nenhum resultado encontrado")
                    return ""

                # Concatena todo o texto reconhecido
                text_lines = []
                for line in result[0]:
                    if line and len(line) > 0:
                        text_lines.append(line[1][0])  # line[1][0] é o texto

                print(f"[OCR] {len(text_lines)} linhas extraídas")
                return "\n".join(text_lines)

        except Exception as e:
            logger.error(f"Erro ao extrair texto de {image_path}: {e}")
            print(f"[OCR] ERRO: {e}")
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
