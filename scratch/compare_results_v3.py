import csv
import os
import re

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

# 1. Carrega o Gabarito (Chave: idParcela)
goal_data = {}
try:
    with open(goal_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extrai o ID da parcela do nome do arquivo: doc_66255_p1.pdf -> 66255
            match = re.search(r'doc_(\d+)_p', row['arquivo'])
            if match:
                pid = match.group(1)
                if pid not in goal_data: goal_data[pid] = []
                goal_data[pid].append(row)
except Exception as e:
    print(f"Erro ao carregar gabarito: {e}")

# 2. Carrega o Motor e tenta casar
print(f"{'ID/URL':<20} | {'GABARITO':<12} | {'MOTOR':<12} | {'STATUS'}")
print("-" * 80)

sucessos = 0
divergencias = 0
desconhecidos = 0
total = 0

try:
    with open(motor_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('Origem', '')
            val_motor_raw = row.get('Valor', '0').replace('R$', '').replace('.', '').replace(',', '.').strip()
            val_motor = float(val_motor_raw) if val_motor_raw else 0.0
            
            # Tenta achar o ID da parcela na URL
            pid = None
            p_match = re.search(r'idParcela=(\d+)', url)
            if p_match:
                pid = p_match.group(1)
            
            # Se achou o ID, compara
            if pid and pid in goal_data:
                total += 1
                g_rows = goal_data[pid]
                g_vals = [float(r['valor']) for r in g_rows]
                g_max = max(g_vals) if g_vals else 0.0
                
                if abs(g_max - val_motor) < 0.1:
                    sucessos += 1
                    # print(f"{pid:<20} | {g_max:<12.2f} | {val_motor:<12.2f} | OK")
                else:
                    print(f"{pid:<20} | {g_max:<12.2f} | {val_motor:<12.2f} | DIVERGENTE")
                    divergencias += 1
            else:
                # Se não tem idParcela, pode ser um link direto. 
                # Vamos tentar casar pelo VALOR se for único (heurística desesperada)
                pass

except Exception as e:
    print(f"Erro ao processar motor: {e}")

print("-" * 80)
print(f"RESUMO DA OPERAÇÃO:")
print(f"✅ Batidos: {sucessos}")
print(f"⚠️ Divergentes: {divergencias}")
if (sucessos + divergencias) > 0:
    print(f"🎯 Assertividade: {(sucessos/(sucessos+divergencias))*100:.2f}%")
else:
    print("Nenhum match direto por idParcela encontrado.")
