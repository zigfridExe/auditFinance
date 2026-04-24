import csv
import os

goal_path = r"c:\manutencao\objetivoExtracao.csv"
motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

def load_csv(path, key_col):
    data = {}
    try:
        with open(path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normaliza o nome do arquivo para comparação
                key = os.path.basename(row[key_col])
                data[key] = row
    except Exception as e:
        print(f"Erro ao carregar {path}: {e}")
    return data

# Mapeia colunas (Motor usa 'Arquivo', 'Data', 'Valor')
# Gabarito usa 'arquivo', 'data', 'valor'
goal_data = load_csv(goal_path, "arquivo")
motor_data = load_csv(motor_path, "Arquivo")

print(f"{'ARQUIVO':<30} | {'GABARITO':<10} | {'MOTOR':<10} | {'STATUS'}")
print("-" * 70)

divergencias = 0
sucessos = 0
total = 0

for file, g_row in goal_data.items():
    total += 1
    m_row = motor_data.get(file)
    
    if not m_row:
        print(f"{file[:30]:<30} | {g_row['valor']:<10} | {'MISSING':<10} | ❌ NÃO PROCESSADO")
        divergencias += 1
        continue
    
    # Limpa valores para comparação numérica
    try:
        g_val = float(g_row['valor'])
        # Motor salva valor formatado ou string? 
        m_val_raw = m_row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
        m_val = float(m_val_raw) if m_val_raw else 0.0
    except:
        m_val = 0.0
        g_val = float(g_row['valor'])

    if abs(g_val - m_val) < 0.01:
        # Sucesso
        sucessos += 1
    else:
        print(f"{file[:30]:<30} | {g_val:<10.2f} | {m_val:<10.2f} | ⚠️ VALOR DIVERGENTE")
        divergencias += 1

print("-" * 70)
print(f"RESUMO: {sucessos} Sucessos | {divergencias} Divergências | Total: {total}")
accuracy = (sucessos/total)*100 if total > 0 else 0
print(f"PRECISÃO DO MOTOR: {accuracy:.2f}%")
