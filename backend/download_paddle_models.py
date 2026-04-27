"""
Script para pré-baixar modelos do PaddleOCR
Execute este script uma vez para baixar todos os modelos necessários
"""

import os
import sys

def download_models():
    print("Iniciando download dos modelos PaddleOCR...")

    try:
        from paddleocr import PaddleOCR

        # Força inicialização para baixar modelos
        print("Baixando modelo de detecção de texto...")
        # Tenta sem use_angle_cls para evitar problemas de CPU
        ocr = PaddleOCR(lang='pt')

        print("Modelos baixados com sucesso!")
        print("\nModelos serão salvos em:")
        print("~/.paddleocr/")
        print("~/.paddleocr/whl/")
        print("~/.paddleocr/whl/det/")
        print("~/.paddleocr/whl/rec/")
        print("~/.paddleocr/whl/cls/")

    except ImportError:
        print("ERRO: paddleocr não está instalado")
        print("Execute: pip install paddleocr paddlepaddle")
        sys.exit(1)
    except Exception as e:
        print(f"ERRO: {e}")
        print("\nSua CPU pode não ser compatível com PaddlePaddle.")
        print("Sugestão: Use Tesseract OCR como alternativa")
        sys.exit(1)

if __name__ == "__main__":
    download_models()
