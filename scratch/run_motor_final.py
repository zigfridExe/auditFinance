import os
import csv
from datetime import datetime
from src.core.pdf_processor import PDFProcessor
from src.core.data_extractor import DataExtractor

source_dir = r"c:\manutencao\auditFinance\backend\teste\janeiro26"
output_file = r"c:\manutencao\auditFinance\extracao_janeiro26_FINAL.csv"

extractor = DataExtractor()
processor = PDFProcessor()

results = []
files = [f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')]
print(f"Motor iniciando extracao de {len(files)} arquivos (Modo IA-Correct ativado)...")

for i, filename in enumerate(files):
    path = os.path.join(source_dir, filename)
    try:
        text = processor.extract_text(path)
        # Passando o filename para ativar a camada de correcao de IA
        data = extractor.extract(text, filename=filename)
        
        results.append({
            "Tipo": "Anexo",
            "Data": data["data"],
            "Categoria": data["categoria"],
            "Valor": data["valor"],
            "Descricao": data["descricao"],
            "Origem": filename,
            "Erro": ""
        })
    except Exception as e:
        results.append({"Origem": filename, "Erro": str(e)})

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["Tipo", "Data", "Categoria", "Valor", "Descricao", "Origem", "Erro"])
    writer.writeheader()
    writer.writerows(results)

print(f"Extracao 100% concluida! Arquivo: {output_file}")
