import sys
import os
import pdfplumber
import re

# Adiciona o caminho do backend para importar os módulos
sys.path.append(r"c:\manutencao\auditFinance\backend\src")

from core.data_extractor import DataExtractor

def debug_cpfl():
    extractor = DataExtractor()
    file_path = r"c:\manutencao\auditFinance\backend\teste\dezembro25\0983fbed-2117-4e56-a7e7-c85859922b10.pdf"
    
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += (page.extract_text() or "") + "\n"
    
    doc_type = extractor.classify(text)
    print(f"CLASSIFICADO COMO: {doc_type}")
    
    config = extractor.patterns.get(doc_type)
    for pattern in config["valor"]:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"MATCH COM PADRÃO: {pattern}")
            print(f"VALOR BRUTO: {match.group(1)}")
            break

if __name__ == "__main__":
    debug_cpfl()
