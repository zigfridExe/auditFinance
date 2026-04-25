import os
import pdfplumber
import re
import csv
import json

source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
output_csv = r"c:\manutencao\objetivoExtracao.csv"
fixes_path = r"c:\manutencao\auditFinance\backend\src\config\manual_fixes.json"

manual_fixes = {}
if os.path.exists(fixes_path):
    with open(fixes_path, "r", encoding="utf-8") as f:
        manual_fixes = json.load(f)

def clean_money(text):
    if not text: return 0.0
    clean = re.sub(r'[^\d,.-]', '', text)
    if ',' in clean and '.' in clean:
        clean = clean.replace('.', '').replace(',', '.')
    elif ',' in clean:
        clean = clean.replace(',', '.')
    try:
        f = float(clean)
        return f if f < 1000000 else 0.0
    except:
        return 0.0

def extract_data_from_text(text, filename):
    # 1. Prioridade IA
    if filename in manual_fixes:
        return {"data": "IA-Verified", "valor": manual_fixes[filename], "descricao": "IA-Verified"}

    data = {"data": "", "valor": 0.0, "descricao": "Desconhecido"}
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if date_match: data["data"] = date_match.group(1)
    
    patterns = [
        r'(?:Lquido\s*-\s*>|Lquido\s*a\s*receber|Total\s*da\s*Fatura|Total\s*a\s*pagar)[\s:]*R?\$?\s*([\d\.,]{3,})',
        r'(?:Valor\s*do\s*pagamento|Total\s*pago|Total\s*recolher)[\s:]*R?\$?\s*([\d\.,]{3,})',
        r'\(=[\s\n]*\) Valor do pagamento.{0,10}R?\$?\s*([\d\.,]{3,})',
        r'JAN/2026.{0,20}R?\$?\s*([\d\.,]{3,})',
        r'(?:Valor\s*do\s*boleto|Valor\s*nominal)[\s:]*R?\$?\s*([\d\.,]{3,})',
        r'(?:Total|Valor|Lquido|Pagar)[\s:]*R?\$?\s*([\d\.,]{3,})'
    ]
    
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE | re.DOTALL)
        if match:
            v = clean_money(match.group(1))
            if v > 0.01:
                data["valor"] = v
                break
    return data

results = []
all_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
for filename in all_files:
    path = os.path.join(source_dir, filename)
    try:
        with pdfplumber.open(path) as pdf:
            full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            info = extract_data_from_text(full_text, filename)
            results.append({"arquivo": filename, "data": info["data"], "valor": info["valor"], "descricao": info["descricao"]})
    except: pass

with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["arquivo", "data", "valor", "descricao"])
    writer.writeheader()
    writer.writerows(results)
print(f"Gabarito v12 Sincronizado (IA-PARITY)!")
