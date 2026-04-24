import csv
import re

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

print("--- BUSCANDO ID 66255 NO GABARITO ---")
with open(goal_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        match = re.search(r'doc_(\d+)_p', row['arquivo'])
        if match and match.group(1) == '66255':
            print(f"ACHOU NO GABARITO: {row}")

print("\n--- BUSCANDO ID 66255 NO MOTOR ---")
with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row.get('Origem', '')
        match = re.search(r'idParcela=(\d+)', url)
        if match and match.group(1) == '66255':
            print(f"ACHOU NO MOTOR: {row}")
