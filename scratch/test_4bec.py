import sys
import os
import pdfplumber

# Adiciona o caminho do backend para importar os módulos
sys.path.append(r"c:\manutencao\auditFinance\backend\src")

from core.data_extractor import DataExtractor

def test_extraction():
    extractor = DataExtractor()
    test_files = [
        r"c:\manutencao\auditFinance\backend\teste\dezembro25\4bec9601-82c5-4705-a8a2-34fda942057b.pdf"
    ]
    
    for file_path in test_files:
        print(f"\n>>> TESTANDO: {os.path.basename(file_path)}")
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        
        result = extractor.extract(text)
        print(f"CATEGORIA: {result['categoria']}")
        print(f"DATA:      {result['data']}")
        print(f"VALOR:     {result['valor']}")

if __name__ == "__main__":
    test_extraction()
