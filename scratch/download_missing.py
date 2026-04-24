import csv
import subprocess
import os

motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"
goal_path = r"c:\manutencao\objetivoExtracao.csv"
output_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"

# Pega o que ja temos no gabarito
goal_vals = set()
if os.path.exists(goal_path):
    with open(goal_path, mode='r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            goal_vals.add(float(row['valor']))

print("Iniciando download dos arquivos faltantes...")

with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        try:
            val_raw = row['Valor'].replace('R$', '').replace('.', '').replace(',', '.').strip()
            val = float(val_raw)
            if val > 0 and val not in goal_vals:
                url = row['Origem']
                # Extrai um ID unico para o nome
                fid = i
                if "id=" in url:
                    fid = url.split("id=")[1].split("&")[0]
                
                filename = f"missing_{fid}.pdf"
                dest = os.path.join(output_dir, filename)
                
                print(f"Baixando: {val} -> {filename}")
                # Usa curl.exe para garantir
                cmd = f'curl.exe -L -s -o "{dest}" "{url}"'
                subprocess.run(cmd, shell=True)
        except:
            pass

print("Downloads concluidos!")
