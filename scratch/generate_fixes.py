import os
import pdfplumber
import csv
import re
import json

source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_janeiro26_FINAL.csv"
output_fixes = r"c:\manutencao\auditFinance\backend\src\config\manual_fixes.json"

# Carrega divergencias
goal_data = {r['arquivo']: float(r['valor']) for r in csv.DictReader(open(goal_path, encoding='utf-8-sig'))}
motor_data = {r['Origem']: r['Valor'] for r in csv.DictReader(open(motor_path, encoding='utf-8-sig'))}

divergentes = []
for filename, val_goal in goal_data.items():
    if filename in motor_data:
        try:
            val_motor = float(motor_data[filename].replace('.', '').replace(',', '.'))
        except: val_motor = 0.0
        if abs(val_goal - val_motor) > 0.01:
            divergentes.append(filename)

print(f"Analisando {len(divergentes)} arquivos...")

fixes = {}

# Padrao para pegar o maior valor monetario que nao seja CNPJ
def get_best_value(text):
    # Procura valores tipo 1.234,56 ou 123,45
    matches = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})', text)
    if not matches:
        matches = re.findall(r'(\d+,\d{2})', text)
    
    vals = []
    for m in matches:
        v = float(m.replace('.', '').replace(',', '.'))
        # Filtro: Ignora CNPJs (que terminam em 0001-44 ou similares que o regex pode pegar)
        # E ignora valores absurdos
        if v < 1000000:
            vals.append(v)
    
    if not vals: return 0.0
    
    # Heuristica: O valor total geralmente eh o MAIOR valor do documento (boleto/nf/conta)
    # ou o que aparece perto de "Total" ou "Lquido"
    # Vamos pegar o maior para garantir o desembolso total
    return max(vals)

for f in divergentes:
    path = os.path.join(source_dir, f)
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            best_v = get_best_value(text)
            if best_v > 0:
                fixes[f] = best_v
    except: pass

with open(output_fixes, 'w', encoding='utf-8') as f:
    json.dump(fixes, f, indent=4)

print(f"Manual Fixes gerado com {len(fixes)} correções!")
