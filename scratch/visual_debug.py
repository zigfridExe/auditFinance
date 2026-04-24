import csv

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

print("--- AMOSTRA GABARITO (Top 10) ---")
with open(goal_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        print(f"GAB: {row['valor']} | {row['data']} | {row['arquivo']}")
        if i > 10: break

print("\n--- AMOSTRA MOTOR (Top 10) ---")
with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        val_raw = row.get('Valor', '0').replace('R$', '').replace('.', '').replace(',', '.').strip()
        print(f"MOT: {val_raw} | {row.get('Data')} | {row.get('Origem')[:50]}")
        if i > 10: break
