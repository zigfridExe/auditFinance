import pdfplumber
import sys

files = [
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\ISSQN SERVIÇOS TOMADOS - 112025.pdf",
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\Vidas reais (3).pdf",
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\NF - 128623.pdf"
]

for file_path in files:
    print(f"\n{'='*20}\nARQUIVO: {file_path}\n{'='*20}")
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"--- PAGINA {i+1} ---")
                print(page.extract_text())
    except Exception as e:
        print(f"Erro ao abrir {file_path}: {e}")
