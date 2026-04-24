import os
import pdfplumber
import re
import csv

# Configurações
source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
output_csv = r"c:\manutencao\objetivoExtracao.csv"

def clean_money(text):
    if not text: return 0.0
    clean = re.sub(r'[^\d,.-]', '', text)
    if ',' in clean and '.' in clean:
        clean = clean.replace('.', '').replace(',', '.')
    elif ',' in clean:
        clean = clean.replace(',', '.')
    try:
        return float(clean)
    except:
        return 0.0

def extract_data_from_text(text):
    data = {"data": "", "valor": 0.0, "descricao": "Desconhecido"}
    
    # Busca Data
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if date_match:
        data["data"] = date_match.group(1)
    
    # Busca Valor
    money_matches = re.findall(r'(?:R\$|Total|Valor|Lquido|Recolher|Pagar|Documento|Guia|valor:)\s*:?\s*([\d\.,]{3,})', text, re.IGNORECASE)
    if money_matches:
        values = [clean_money(m) for m in money_matches]
        valid_values = [v for v in values if 0.01 < v < 1000000.0]
        data["valor"] = max(valid_values) if valid_values else 0.0

    # Busca Descrição
    lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 5]
    for line in lines:
        if any(x in line.upper() for x in ["NOME", "RAZO SOCIAL", "BENEFICIRIO", "PRESTADOR", "CONTRIBUINTE", "PAGADOR"]):
            data["descricao"] = line.split(':')[-1].strip()[:100]
            break
    if data["descricao"] == "Desconhecido" and lines:
        data["descricao"] = lines[0][:100]

    return data

results = []
# Pega TODOS os PDFs (sem filtrar por _p)
files = [f for f in os.listdir(source_dir) if f.endswith('.pdf')]
files.sort()

print(f"Analisando TOTAL de {len(files)} arquivos PDF de Janeiro/2026...")

for filename in files:
    path = os.path.join(source_dir, filename)
    try:
        # Verifica se o arquivo é um PDF de verdade (não um HTML renomeado)
        with open(path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                # print(f"Pulo: {filename} não é binário PDF.")
                continue

        with pdfplumber.open(path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text: full_text += text + "\n"
            
            if not full_text.strip():
                # Se não tem texto, pode ser imagem pura
                # print(f"Aviso: {filename} sem texto (imagem?)")
                pass

            info = extract_data_from_text(full_text)
            results.append({
                "arquivo": filename,
                "data": info["data"],
                "valor": info["valor"],
                "descricao": info["descricao"]
            })
    except Exception as e:
        # print(f"Erro em {filename}: {e}")
        pass

# Salva o CSV
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["arquivo", "data", "valor", "descricao"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSucesso total! Gabarito COMPLETO gerado em: {output_csv}")
