import csv
import os
import re

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

def get_id_from_url(url):
    if not url: return None
    # Tenta idParcela
    match = re.search(r'idParcela=(\d+)', url)
    if match: return match.group(1)
    # Tenta id do downloadarquivo
    match = re.search(r'id=(\d+)', url)
    if match: return f"id_{match.group(1)}"
    return None

def get_id_from_filename(filename):
    # doc_66255_p1.pdf -> 66255
    match = re.search(r'doc_(\d+)_p', filename)
    if match: return match.group(1)
    return None

# Carrega Gabarito agrupando por ID de parcela (pode ter vários arquivos por parcela)
goal_data = {}
try:
    with open(goal_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = get_id_from_filename(row['arquivo'])
            if pid:
                if pid not in goal_data: goal_data[pid] = []
                goal_data[pid].append(row)
except Exception as e:
    print(f"Erro Gabarito: {e}")

# Carrega Motor
motor_results = []
try:
    with open(motor_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = get_id_from_url(row['Origem'])
            if pid:
                motor_results.append({"id": pid, "row": row})
except Exception as e:
    print(f"Erro Motor: {e}")

print(f"{'ID PARCELA':<12} | {'GABARITO (MAX)':<15} | {'MOTOR':<10} | {'STATUS'}")
print("-" * 75)

sucessos = 0
divergencias = 0
total = 0

for m_item in motor_results:
    pid = m_item['id']
    m_row = m_item['row']
    total += 1
    
    g_rows = goal_data.get(pid)
    if not g_rows:
        # Tenta busca parcial se for ID de download
        print(f"{pid:<12} | {'???':<15} | {m_row['Valor']:<10} | SEM GABARITO")
        continue

    # Pega o maior valor do gabarito para aquela parcela (geralmente é o que o motor deve achar)
    g_vals = [float(r['valor']) for r in g_rows]
    g_max = max(g_vals) if g_vals else 0.0
    
    m_val_raw = m_row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
    m_val = float(m_val_raw) if m_val_raw else 0.0

    if abs(g_max - m_val) < 0.1:
        sucessos += 1
    else:
        print(f"{pid:<12} | {g_max:<15.2f} | {m_val:<10.2f} | DIVERGENTE")
        divergencias += 1

print("-" * 75)
print(f"RESULTADO: {sucessos} Batidos | {divergencias} Divergentes | Total Analisado: {total}")
if total > 0:
    print(f"ASSERTIVIDADE: {(sucessos/total)*100:.2f}%")
