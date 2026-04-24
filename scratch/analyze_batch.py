import sys
import os
import csv
import pdfplumber

# Adiciona o caminho do backend para importar os módulos
sys.path.append(r"c:\manutencao\auditFinance\backend\src")

from core.pdf_processor import PDFProcessor
from core.data_extractor import DataExtractor

def analyze_batch():
    processor = PDFProcessor()
    extractor = DataExtractor()
    folder_path = r"c:\manutencao\auditFinance\backend\teste\dezembro25"
    output_file = r"c:\manutencao\auditFinance\scratch\analise_dezembro.csv"
    
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    results = []
    
    print(f"Processando {len(files)} arquivos...")
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            text = processor.extract_text(file_path)
            data = extractor.extract(text)
            
            # Se não pegou valor ou deu erro, marca para inspeção
            status = "OK"
            if not data['valor'] or data['valor'] == "0,00":
                status = "FALHA_VALOR"
            
            results.append({
                "arquivo": filename,
                "categoria": data['categoria'],
                "data": data['data'],
                "valor": data['valor'],
                "status": status
            })
        except Exception as e:
            results.append({
                "arquivo": filename,
                "status": f"ERRO_PROCESSAMENTO: {str(e)}"
            })

    # Salva o resultado para análise
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["arquivo", "categoria", "data", "valor", "status"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Análise concluída. Resultado salvo em: {output_file}")
    
    # Mostra as falhas no console para ação imediata
    falhas = [r for r in results if r['status'] != "OK"]
    if falhas:
        print(f"\nDetectadas {len(falhas)} falhas:")
        for f in falhas:
            print(f"- {f['arquivo']}: {f['status']} ({f.get('categoria', 'N/A')})")
    else:
        print("\nTodos os arquivos foram processados com sucesso!")

if __name__ == "__main__":
    analyze_batch()
