import csv
import os

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

# Carrega todos os valores/datas do Gabarito
goal_pool = set()
try:
    with open(goal_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = float(row['valor'])
            if val > 0:
                goal_pool.add((val, row['data']))
except Exception as e:
    print(f"Erro Gabarito: {e}")

sucessos = 0
falhas = 0
total_motor = 0

with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        val_raw = row.get('Valor', '0').replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            val = float(val_raw) if val_raw else 0.0
        except:
            val = 0.0
        data = row.get('Data', '')
        
        if val > 0:
            total_motor += 1
            if (val, data) in goal_pool or any(abs(v - val) < 0.01 for v, d in goal_pool):
                sucessos += 1
            else:
                falhas += 1

print("-" * 50)
print(f"RESUMO FINAL (JANEIRO/2026):")
print(f"Itens Batidos: {sucessos}")
print(f"Itens Divergentes: {falhas}")
if total_motor > 0:
    print(f"Assertividade do Motor: {(sucessos/total_motor)*100:.2f}%")
print("-" * 50)
