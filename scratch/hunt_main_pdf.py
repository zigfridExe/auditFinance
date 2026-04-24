import csv
import os
import pdfplumber

# Arquivos
main_pdf = r"c:\manutencao\auditFinance\doc\01__Prestao_de_contas_Janeiro_2026.pdf"
motor_csv = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"
goal_csv = r"c:\manutencao\objetivoExtracao.csv"

# 1. Carrega o que o motor achou de divergente
motor_vals = []
goal_vals = set()

with open(goal_csv, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        goal_vals.add(float(row['valor']))

divergentes = []
with open(motor_csv, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        val_raw = row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            val = float(val_raw)
            if val > 0 and val not in goal_vals:
                divergentes.append(val)
        except: pass

print(f"Buscando {len(divergentes)} valores divergentes no PDF Principal...")

# 2. Busca no PDF Principal
found_in_main = {}
try:
    with pdfplumber.open(main_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            for val in divergentes:
                val_str = f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') # Formato brasileiro
                if val_str in text:
                    if val not in found_in_main: found_in_main[val] = []
                    found_in_main[val].append(i + 1)
except Exception as e:
    print(f"Erro ao ler PDF Principal: {e}")

print("\n--- RESULTADO DA BUSCA NO PDF PRINCIPAL ---")
for val, pages in found_in_main.items():
    print(f"Valor R$ {val:.2f} encontrado na(s) página(s): {pages}")

print(f"\nTotal de valores recuperados do PDF Principal: {len(found_in_main)} de {len(divergentes)}")
