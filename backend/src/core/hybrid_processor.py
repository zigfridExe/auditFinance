"""
Hybrid PDF Processor
Pipeline inteligente que escolhe o melhor método baseado no tipo de PDF
"""

import logging
from typing import Dict, Any, Optional
from .pdf_type_detector import PDFTypeDetector, PDFType
from .ocr_processor import OCRProcessor
from .semantic_structurer import SemanticStructurer
from .data_extractor import DataExtractor

logger = logging.getLogger(__name__)


class HybridProcessor:
    def __init__(self):
        """Inicializa todos os processadores (lazy)"""
        self._type_detector = None
        self._ocr_processor = None
        self._semantic_structurer = None
        self._data_extractor = None

    @property
    def type_detector(self):
        if self._type_detector is None:
            self._type_detector = PDFTypeDetector()
        return self._type_detector

    @property
    def ocr_processor(self):
        if self._ocr_processor is None:
            self._ocr_processor = OCRProcessor()
        return self._ocr_processor

    @property
    def semantic_structurer(self):
        if self._semantic_structurer is None:
            self._semantic_structurer = SemanticStructurer()
        return self._semantic_structurer

    @property
    def data_extractor(self):
        if self._data_extractor is None:
            self._data_extractor = DataExtractor()
        return self._data_extractor

    def process(self, pdf_path: str) -> Dict[str, Any]:
        """
        Processa PDF usando o pipeline híbrido
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dicionário com dados extraídos
        """
        logger.info(f"Processando PDF: {pdf_path}")
        
        # 1. Detecta tipo de PDF
        pdf_type, digital_text = self.type_detector.detect(pdf_path)
        logger.info(f"Tipo de PDF detectado: {pdf_type.value}")
        
        # 2. Processa baseado no tipo
        if pdf_type == PDFType.DIGITAL:
            return self._process_digital(digital_text)
        else:
            return self._process_scanned(pdf_path)

    def _process_digital(self, text: str) -> Dict[str, Any]:
        """
        Processa PDF digital usando regex (método atual)
        
        Args:
            text: Texto extraído do PDF
            
        Returns:
            Dados estruturados
        """
        logger.info("Usando pipeline digital (pypdf + regex)")
        
        try:
            # Usa o DataExtractor existente (regex)
            result = self.data_extractor.extract(text)
            
            # Adiciona metadados
            result["extraction_method"] = "digital_regex"
            result["extraction_success"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no pipeline digital: {e}")
            return {
                "data": None,
                "valor": None,
                "descricao": "Erro extração digital",
                "categoria": "Erro",
                "extraction_method": "digital_regex",
                "extraction_success": False
            }

    def _process_scanned(self, pdf_path: str) -> Dict[str, Any]:
        """
        Processa PDF escaneado usando OCR + LLM
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dados estruturados
        """
        logger.info("Usando pipeline escaneado (OCR + LLM)")
        
        try:
            # 1. Extrai texto via OCR
            ocr_text = self.ocr_processor.extract_text_from_pdf(pdf_path)
            
            if not ocr_text or len(ocr_text.strip()) < 10:
                logger.warning("OCR não extraiu texto suficiente")
                return self._fallback_to_regex(pdf_path)
            
            logger.info(f"Texto extraído via OCR: {len(ocr_text)} caracteres")
            
            # 2. Tenta estruturar com Ollama
            if self.semantic_structurer.is_available():
                try:
                    result = self.semantic_structurer.structure(ocr_text)
                    result["extraction_method"] = "scanned_ollama"
                    result["extraction_success"] = True
                    logger.info("Estruturação com Ollama bem-sucedida")
                    return result
                except Exception as e:
                    logger.warning(f"Ollama falhou: {e}, usando fallback regex")
            else:
                logger.warning("Ollama não disponível, usando fallback regex")
            
            # 3. Fallback: usa regex no texto do OCR
            return self._extract_from_ocr_text(ocr_text)
            
        except Exception as e:
            logger.error(f"Erro no pipeline escaneado: {e}")
            return self._fallback_to_regex(pdf_path)

    def _extract_from_ocr_text(self, ocr_text: str) -> Dict[str, Any]:
        """
        Usa regex no texto extraído via OCR
        
        Args:
            ocr_text: Texto do OCR
            
        Returns:
            Dados estruturados
        """
        try:
            result = self.data_extractor.extract(ocr_text)
            result["extraction_method"] = "scanned_ocr_regex"
            result["extraction_success"] = True
            return result
        except Exception as e:
            logger.error(f"Erro no fallback regex: {e}")
            return {
                "data": None,
                "valor": None,
                "descricao": "Erro extração OCR",
                "categoria": "Erro",
                "extraction_method": "scanned_ocr_regex",
                "extraction_success": False
            }

    def _fallback_to_regex(self, pdf_path: str) -> Dict[str, Any]:
        """
        Fallback final: tenta extrair do PDF como se fosse digital
        (alguns PDFs "escaneados" têm camada de texto)
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dados estruturados
        """
        logger.warning("Usando fallback final (tentando extrair texto direto)")
        
        try:
            import pypdf
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                
                if text and len(text.strip()) > 10:
                    result = self.data_extractor.extract(text)
                    result["extraction_method"] = "fallback_regex"
                    result["extraction_success"] = True
                    return result
        except Exception as e:
            logger.error(f"Fallback falhou: {e}")
        
        return {
            "data": None,
            "valor": None,
            "descricao": "Não foi possível extrair dados",
            "categoria": "Erro",
            "extraction_method": "fallback_failed",
            "extraction_success": False
        }
