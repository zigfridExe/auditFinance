import os
import pdfplumber

target = "562.33"
found = False
source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"

print(f"Buscando valor {target} nos PDFs...")

for f in os.listdir(source_dir):
    if f.endswith('.pdf'):
        try:
            path = os.path.join(source_dir, f)
            with pdfplumber.open(path) as pdf:
                text = "".join([p.extract_text() or "" for p in pdf.pages])
                if target in text:
                    print(f"ACHADO: {f}")
                    found = True
        except:
            pass

if not found:
    print("Valor nao encontrado em nenhum PDF.")
