# mineradorDeContas/main.py

import os
import shutil
from datetime import datetime

# Importa os módulos que criamos
from .pdf_processor import extract_text_from_pdf, extract_links_from_pdf, download_pdf
from .data_extractor import DataExtractor
from .csv_generator import generate_consolidated_csv
from .utils import clean_text, normalize_value # Importa as funções de utils

# Define o caminho base do projeto (onde o GEMINI.md e a pasta mineradorDeContas estão)
# Isso é importante para que os caminhos relativos funcionem corretamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # mineradorDeContas/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # I:/Meu Drive/Documentos/Condominio/

TEMP_DIR = os.path.join(BASE_DIR, 'temp')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
PATTERNS_FILE = os.path.join(CONFIG_DIR, 'patterns.json')
OUTPUT_DIR = PROJECT_ROOT # O CSV final será salvo na raiz do projeto

def setup_environment():
    """
    Configura o ambiente, garantindo que as pastas necessárias existam.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    # Cria um patterns.json de exemplo se não existir
    if not os.path.exists(PATTERNS_FILE):
        print(f"Criando arquivo de padrões de exemplo em: {PATTERNS_FILE}")
        example_patterns = {
            "generico": {
                "data": ["Data:\s*(\d{2}/\d{2}/\d{4})", "(\d{2}/\d{2}/\d{4})"],
                "valor": ["Total:\s*([\d\.,]+)", "R\\$\s*([\d\.,]+)"],
                "descricao": ["Referente a:\s*(.*)", "Serviço:\s*(.*)"],
                "categoria": {
                    "Agua": ["água", "saneamento"],
                    "Luz": ["energia", "eletricidade"],
                    "Internet": ["internet", "banda larga"],
                    "Manutenção": ["manutenção", "jardim"]
                }
            },
            "conta_luz": {
                "identificadores": ["conta de energia", "eletropaulo", "enel"],
                "data": ["Vencimento:\s*(\d{2}/\d{2}/\d{4})"],
                "valor": ["Valor a Pagar\\s*R\\$\s*([\d\.,]+)"],
                "descricao": ["Consumo de Energia Elétrica"],
                "categoria": { "Luz": ["energia", "eletricidade"] }
            }
        }
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(example_patterns, f, indent=4, ensure_ascii=False)

def process_pdf_document(pdf_path, data_extractor_instance, all_extracted_data):
    """
    Processa um único documento PDF: extrai texto, classifica, extrai dados.
    """
    print(f"Processando PDF: {pdf_path}")
    text_content = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(text_content)

    if not cleaned_text:
        print(f"Não foi possível extrair texto de {pdf_path}. Pulando.")
        return

    doc_type = data_extractor_instance.classify_document(cleaned_text)
    extracted_item = data_extractor_instance.extract_financial_data(cleaned_text, doc_type)
    
    # Adiciona o caminho do PDF original para rastreamento
    extracted_item['origem_pdf'] = os.path.basename(pdf_path)
    
    # Normaliza o valor se foi extraído como string
    if isinstance(extracted_item['valor'], str):
        extracted_item['valor'] = normalize_value(extracted_item['valor'])

    all_extracted_data.append(extracted_item)
    print(f"Dados extraídos de {os.path.basename(pdf_path)}: {extracted_item}")


def main(main_pdf_path):
    """
    Função principal para orquestrar a mineração de dados.
    """
    setup_environment()
    data_extractor = DataExtractor(patterns_file=PATTERNS_FILE)
    all_extracted_data = []

    # 1. Processar o PDF principal
    process_pdf_document(main_pdf_path, data_extractor, all_extracted_data)

    # 2. Extrair links do PDF principal e baixar PDFs anexos
    print(f"\nExtraindo links do PDF principal: {main_pdf_path}")
    linked_pdf_urls = extract_links_from_pdf(main_pdf_path)
    downloaded_pdf_paths = []

    for i, url in enumerate(linked_pdf_urls):
        # Gera um nome de arquivo único para o PDF baixado
        filename = f"linked_doc_{i+1}_{os.path.basename(url).split('?')[0]}"
        output_file_path = os.path.join(TEMP_DIR, filename)
        print(f"Tentando baixar: {url} para {output_file_path}")
        if download_pdf(url, output_file_path):
            downloaded_pdf_paths.append(output_file_path)

    # 3. Processar os PDFs baixados
    print("\nProcessando PDFs baixados...")
    for pdf_path in downloaded_pdf_paths:
        process_pdf_document(pdf_path, data_extractor, all_extracted_data)

    # 4. Gerar o CSV consolidado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv_filename = f"prestacao_contas_consolidado_{timestamp}.csv"
    output_csv_path = os.path.join(OUTPUT_DIR, output_csv_filename)
    
    print(f"\nGerando CSV consolidado em: {output_csv_path}")
    generate_consolidated_csv(all_extracted_data, output_csv_path)

    # 5. Limpar arquivos temporários
    print(f"\nLimpando diretório temporário: {TEMP_DIR}")
    shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True) # Recria a pasta temp vazia

    print("\nProcesso de mineração concluído!")

if __name__ == '__main__':
    # Exemplo de uso:
    # O caminho para o PDF principal de prestação de contas
    # Substitua pelo caminho real do seu arquivo de janeiro
    main_pdf = os.path.join(PROJECT_ROOT, '01__Prestao_de_contas_Janeiro_2026.pdf')
    
    # Para o teste, vamos criar um arquivo patterns.json de exemplo
    # Isso já é feito em setup_environment(), mas é bom ter certeza para o __main__
    import json
    setup_environment() # Garante que o patterns.json exista para o DataExtractor

    if os.path.exists(main_pdf):
        main(main_pdf)
    else:
        print(f"Erro: O arquivo PDF principal não foi encontrado em {main_pdf}")
        print("Por favor, verifique o caminho e tente novamente.")
