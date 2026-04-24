import pdfplumber
import sys

files = [
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\0983fbed-2117-4e56-a7e7-c85859922b10.pdf",
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\0efc6709-82bf-4f6a-89e3-e8b62b828130.pdf",
    r"c:\manutencao\auditFinance\backend\teste\dezembro25\4bec9601-82c5-4705-a8a2-34fda942057b.pdf"
]
for file_path in files:
    print(f"=== FILE: {file_path} ===")
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(page.extract_text())

