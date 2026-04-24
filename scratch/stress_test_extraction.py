import sys
import os
import pdfplumber

# Adiciona o caminho do backend para importar os módulos
sys.path.append(r"c:\manutencao\auditFinance\backend\src")

from core.data_extractor import DataExtractor

def test_extraction():
    extractor = DataExtractor()
    test_files = [
        r"c:\manutencao\auditFinance\backend\teste\dezembro25\0983fbed-2117-4e56-a7e7-c85859922b10.pdf",
        r"c:\manutencao\auditFinance\backend\teste\dezembro25\GuiaPagamento_46028481000144_101220251329588949.pdf",
        r"c:\manutencao\auditFinance\backend\teste\dezembro25\1299.pdf",
        r"c:\manutencao\auditFinance\backend\teste\dezembro25\C6Bank-boleto-266712057_251030_185344.pdf"
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
        print(f"DESC:      {result['descricao']}")

if __name__ == "__main__":
    test_extraction()
