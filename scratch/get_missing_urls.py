import csv

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

goal_vals = set()
with open(goal_path, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        goal_vals.add(float(row['valor']))

print("--- URLS FALTANTES ---")
missing_urls = []
with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        try:
            val_raw = row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
            val = float(val_raw)
            if val > 0 and val not in goal_vals:
                print(f"{val} | {row['Origem']}")
                missing_urls.append(row['Origem'])
        except:
            pass
