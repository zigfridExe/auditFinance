import csv
import re

motor_path = r"c:\manutencao\auditFinance\extracao_1777057592486.csv"

with open(motor_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    print("Colunas detectadas:", reader.fieldnames)
    for i, row in enumerate(reader):
        url = row.get('Origem', '')
        p_match = re.search(r'idParcela=(\d+)', url)
        print(f"Linha {i+1}: URL='{url[:50]}...' -> ID extraído: {p_match.group(1) if p_match else 'NADA'}")
        if i > 5: break
