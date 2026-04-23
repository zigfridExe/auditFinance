# mineradorDeContas/csv_generator.py

import pandas as pd
import os

def generate_consolidated_csv(data_list, output_csv_path):
    """
    Gera um arquivo CSV consolidado a partir de uma lista de dicionários de dados financeiros.
    """
    if not data_list:
        print("Nenhum dado para gerar o CSV.")
        return False

    # Define as colunas esperadas para garantir consistência
    columns = [
        "data",
        "descricao",
        "valor",
        "categoria",
        "documento_referencia",
        "tipo_documento",
        "origem_pdf" # Adiciona uma coluna para saber de qual PDF o dado veio
    ]

    # Cria um DataFrame a partir da lista de dicionários
    df = pd.DataFrame(data_list)

    # Garante que todas as colunas esperadas existam, preenchendo com None se ausentes
    for col in columns:
        if col not in df.columns:
            df[col] = None
    
    # Reordena as colunas
    df = df[columns]

    try:
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"CSV gerado com sucesso em: {output_csv_path}")
        return True
    except Exception as e:
        print(f"Erro ao gerar o arquivo CSV {output_csv_path}: {e}")
        return False

if __name__ == '__main__':
    # Exemplo de uso
    sample_data = [
        {
            "data": "15/02/2026",
            "descricao": "Consumo de Energia Elétrica",
            "valor": 125.50,
            "categoria": "Luz",
            "documento_referencia": None,
            "tipo_documento": "conta_luz",
            "origem_pdf": "prestacao_janeiro.pdf"
        },
        {
            "data": "20/01/2026",
            "descricao": "Manutenção de Jardim",
            "valor": 350.00,
            "categoria": "Manutenção",
            "documento_referencia": "REC-001",
            "tipo_documento": "generico",
            "origem_pdf": "recibo_jardim.pdf"
        }
    ]

    output_file = "mineradorDeContas/output_data.csv"
    # Garante que o diretório de saída exista
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    if generate_consolidated_csv(sample_data, output_file):
        print(f"Verifique o arquivo: {output_file}")
    else:
        print("Falha ao gerar CSV de exemplo.")
