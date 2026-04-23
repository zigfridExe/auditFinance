# mineradorDeContas/data_extractor.py

import re
import json
import os

class DataExtractor:
    def __init__(self, patterns_file='mineradorDeContas/config/patterns.json'):
        self.patterns = self._load_patterns(patterns_file)

    def _load_patterns(self, patterns_file):
        """
        Carrega os padrões de expressões regulares de um arquivo JSON.
        """
        try:
            # Ajusta o caminho para ser absoluto ou relativo ao diretório de execução
            # Assumindo que o script principal será executado da raiz do projeto
            # e patterns_file é relativo à raiz do projeto.
            # Se este script for executado diretamente, o caminho pode precisar de ajuste.
            absolute_patterns_file = os.path.join(os.path.dirname(__file__), 'config', os.path.basename(patterns_file))
            
            with open(absolute_patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Arquivo de padrões não encontrado: {absolute_patterns_file}")
            return {}
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON do arquivo de padrões: {absolute_patterns_file}")
            return {}

    def extract_financial_data(self, text_content, document_type="generico"):
        """
        Extrai dados financeiros do conteúdo de texto de um PDF.
        Usa padrões definidos no arquivo JSON.
        """
        extracted_data = {
            "data": None,
            "descricao": None,
            "valor": None,
            "categoria": None,
            "documento_referencia": None,
            "tipo_documento": document_type
        }

        if document_type not in self.patterns:
            print(f"Tipo de documento '{document_type}' não encontrado nos padrões. Usando padrões genéricos.")
            document_type = "generico" # Fallback para genérico

        doc_patterns = self.patterns.get(document_type, {})

        # Extração de Data
        if 'data' in doc_patterns:
            for pattern in doc_patterns['data']:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    extracted_data['data'] = match.group(1) # Assume que o grupo 1 é a data
                    break
        
        # Extração de Valor
        if 'valor' in doc_patterns:
            for pattern in doc_patterns['valor']:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    # Limpa o valor para um formato numérico (ex: remove R$, pontos, troca vírgula por ponto)
                    valor_str = match.group(1).replace('.', '').replace(',', '.')
                    try:
                        extracted_data['valor'] = float(valor_str)
                    except ValueError:
                        extracted_data['valor'] = None
                    break

        # Extração de Descrição (pode ser mais complexa, aqui um exemplo simples)
        if 'descricao' in doc_patterns:
            for pattern in doc_patterns['descricao']:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    extracted_data['descricao'] = match.group(1).strip()
                    break
        
        # Extração de Categoria (pode ser inferida por palavras-chave ou regex)
        if 'categoria' in doc_patterns:
            for category, keywords in doc_patterns['categoria'].items():
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_content, re.IGNORECASE):
                        extracted_data['categoria'] = category
                        break
                if extracted_data['categoria']:
                    break

        # Extração de Documento de Referência
        if 'documento_referencia' in doc_patterns:
            for pattern in doc_patterns['documento_referencia']:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    extracted_data['documento_referencia'] = match.group(1).strip()
                    break

        return extracted_data

    def classify_document(self, text_content):
        """
        Tenta classificar o tipo de documento com base em palavras-chave ou padrões.
        """
        for doc_type, patterns in self.patterns.items():
            if 'identificadores' in patterns:
                for identifier_pattern in patterns['identificadores']:
                    if re.search(identifier_pattern, text_content, re.IGNORECASE):
                        return doc_type
        return "generico" # Retorna genérico se não encontrar um tipo específico

if __name__ == '__main__':
    # Exemplo de uso
    # Primeiro, crie um arquivo config/patterns.json
    # Exemplo de patterns.json:
    # {
    #     "generico": {
    #         "data": ["(\\d{2}/\\d{2}/\\d{4})", "(\\d{2} de [a-zA-Z]+ de \\d{4})"],
    #         "valor": ["R\\$\s*([\\d\\.,]+)", "Total:\\s*([\\d\\.,]+)"],
    #         "descricao": ["Serviço:\\s*(.*)", "Referente a:\\s*(.*)"],
    #         "categoria": {
    #             "Agua": ["água", "saneamento"],
    #             "Luz": ["energia", "eletricidade"],
    #             "Internet": ["internet", "banda larga"]
    #         }
    #     },
    #     "conta_luz": {
    #         "identificadores": ["conta de energia", "eletropaulo", "enel"],
    #         "data": ["Vencimento:\\s*(\\d{2}/\\d{2}/\\d{4})"],
    #         "valor": ["Valor a Pagar\\s*R\\$\s*([\\d\\.,]+)"],
    #         "descricao": ["Consumo de Energia Elétrica"],
    #         "categoria": { "Luz": ["energia", "eletricidade"] }
    #     }
    # }

    # Crie um arquivo de teste para simular o conteúdo de um PDF
    sample_text_luz = """
    CONTA DE ENERGIA - ENEL
    Período: 01/01/2026 a 31/01/2026
    Vencimento: 15/02/2026
    Consumo de Energia Elétrica
    Valor a Pagar R$ 125,50
    """

    sample_text_generico = """
    Recibo de Pagamento
    Data: 20/01/2026
    Referente a: Manutenção de Jardim
    Total: 350,00
    """
    
    # Garante que o diretório config exista para o teste
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Cria um patterns.json de exemplo para o teste
    example_patterns = {
        "generico": {
            "data": ["Data:\\s*(\\d{2}/\\d{2}/\\d{4})", "(\\d{2}/\\d{2}/\\d{4})"],
            "valor": ["Total:\\s*([\\d\\.,]+)", "R\\$\s*([\\d\\.,]+)"],
            "descricao": ["Referente a:\\s*(.*)", "Serviço:\\s*(.*)"],
            "categoria": {
                "Agua": ["água", "saneamento"],
                "Luz": ["energia", "eletricidade"],
                "Internet": ["internet", "banda larga"],
                "Manutenção": ["manutenção", "jardim"]
            }
        },
        "conta_luz": {
            "identificadores": ["conta de energia", "eletropaulo", "enel"],
            "data": ["Vencimento:\\s*(\\d{2}/\\d{2}/\\d{4})"],
            "valor": ["Valor a Pagar\\s*R\\$\s*([\\d\\.,]+)"],
            "descricao": ["Consumo de Energia Elétrica"],
            "categoria": { "Luz": ["energia", "eletricidade"] }
        }
    }
    
    patterns_file_path = os.path.join(config_dir, 'patterns.json')
    with open(patterns_file_path, 'w', encoding='utf-8') as f:
        json.dump(example_patterns, f, indent=4, ensure_ascii=False)

    extractor = DataExtractor(patterns_file=patterns_file_path)

    print("--- Teste Conta de Luz ---")
    doc_type_luz = extractor.classify_document(sample_text_luz)
    print(f"Documento classificado como: {doc_type_luz}")
    data_luz = extractor.extract_financial_data(sample_text_luz, doc_type_luz)
    print(data_luz)

    print("\n--- Teste Genérico ---")
    doc_type_generico = extractor.classify_document(sample_text_generico)
    print(f"Documento classificado como: {doc_type_generico}")
    data_generico = extractor.extract_financial_data(sample_text_generico, doc_type_generico)
    print(data_generico)
