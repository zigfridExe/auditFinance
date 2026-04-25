import os
import pdfplumber
import csv
import re

source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_janeiro26_FINAL.csv"

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

print(f"Total de Divergências: {len(divergentes)}")
print("Iniciando Extração de Contexto para IA...")

for f in divergentes[:15]: # Primeiras 15 para calibrar
    path = os.path.join(source_dir, f)
    print(f"\n>>>> FILE: {f} <<<<")
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            # Pega as linhas que tem R$ ou valores
            lines = [l.strip() for l in text.split('\n') if "R$" in l or any(c.isdigit() for c in l)]
            for l in lines:
                if len(l) > 10: print(f"  {l}")
    except:
        print("  [Erro ao ler PDF]")
