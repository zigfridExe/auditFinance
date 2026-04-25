import csv

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_janeiro26_FINAL.csv"

# 1. Carrega o Gabarito (Chave: Nome do Arquivo)
goal_data = {}
with open(goal_path, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        goal_data[row['arquivo']] = float(row['valor'])

# 2. Compara com o Motor
sucessos = 0
divergencias = 0
total = 0

print(f"{'ARQUIVO':<30} | {'GABARITO':<12} | {'MOTOR':<12} | {'STATUS'}")
print("-" * 75)

with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        filename = row['Origem']
        if filename in goal_data:
            total += 1
            val_goal = goal_data[filename]
            val_motor_raw = row['Valor'].replace('.', '').replace(',', '.').strip()
            try:
                val_motor = float(val_motor_raw)
            except:
                val_motor = 0.0
            
            # Se ambos forem zero, ignoramos da estatistica de assertividade se quiser, 
            # mas aqui vamos contar como sucesso se baterem.
            if abs(val_goal - val_motor) < 0.01:
                sucessos += 1
            else:
                if val_goal > 0 or val_motor > 0: # So mostra se um dos dois achou algo
                    print(f"{filename[:30]:<30} | {val_goal:<12.2f} | {val_motor:<12.2f} | DIVERGENTE")
                    divergencias += 1

print("-" * 75)
print(f"VEREDITO FINAL JANEIRO/2026:")
print(f"Total de Arquivos Analisados: {total}")
print(f"Sucessos (Match 100%): {sucessos}")
print(f"Divergencias: {divergencias}")
if total > 0:
    print(f"ASSERTIVIDADE FINAL: {(sucessos/total)*100:.2f}%")
print("-" * 75)
