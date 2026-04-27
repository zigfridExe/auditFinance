"""
Tesseract OCR Processor
Alternativa leve ao PaddleOCR para CPUs sem suporte AVX
"""

import pytesseract
from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TesseractOCR:
    def __init__(self, lang: str = "por"):
        """
        Args:
            lang: Idioma para OCR (por = português, eng = inglês)
        """
        self.lang = lang
        self._initialized = False

    def _initialize(self):
        """Verifica se Tesseract está disponível"""
        if self._initialized:
            return

        try:
            pytesseract.get_tesseract_version()
            self._initialized = True
            logger.info("Tesseract OCR inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Tesseract: {e}")
            raise RuntimeError("Tesseract não está instalado ou não está no PATH")

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando Tesseract OCR

        Args:
            image_path: Caminho da imagem

        Returns:
            Texto extraído
        """
        print(f"[TESSERACT] Iniciando extração de {image_path}")
        self._initialize()
        print(f"[TESSERACT] Tesseract inicializado")

        try:
            print(f"[TESSERACT] Carregando imagem...")
            image = Image.open(image_path)
            print(f"[TESSERACT] Executando OCR...")
            text = pytesseract.image_to_string(image, lang=self.lang)
            print(f"[TESSERACT] OCR concluído")
            print(f"[TESSERACT] {len(text)} caracteres extraídos")

            return text.strip()

        except Exception as e:
            logger.error(f"Erro ao extrair texto de {image_path}: {e}")
            print(f"[TESSERACT] ERRO: {e}")
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
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Extrai texto da imagem
                text = pytesseract.image_to_string(img, lang=self.lang)
                all_text.append(text)

            doc.close()
            return "\n\n".join(all_text)

        except Exception as e:
            logger.error(f"Erro ao extrair texto de PDF {pdf_path}: {e}")
            return ""
