# mineradorDeContas/utils.py

import re

def clean_text(text):
    """
    Realiza uma limpeza básica no texto extraído de PDFs.
    Remove múltiplos espaços, quebras de linha extras e caracteres não imprimíveis.
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text)  # Substitui múltiplos espaços/quebras de linha por um único espaço
    text = text.strip()              # Remove espaços no início e fim
    text = ''.join(char for char in text if char.isprintable() or char == '\n') # Remove caracteres não imprimíveis
    return text

def normalize_value(value_str):
    """
    Normaliza uma string de valor monetário para um float.
    Ex: "R$ 1.234,56" -> 1234.56
    """
    if not isinstance(value_str, str):
        return None
    
    # Remove o símbolo da moeda e espaços
    cleaned_value = value_str.replace("R$", "").replace(" ", "").strip()
    
    # Troca o separador de milhar (ponto) por nada e o separador decimal (vírgula) por ponto
    # Isso é comum em padrões brasileiros
    if ',' in cleaned_value and '.' in cleaned_value:
        # Se tiver ambos, assume padrão brasileiro (1.000,00)
        parts = cleaned_value.split(',')
        integer_part = parts[0].replace('.', '')
        decimal_part = parts[1]
        cleaned_value = f"{integer_part}.{decimal_part}"
    elif ',' in cleaned_value:
        # Se tiver só vírgula, assume que é o separador decimal
        cleaned_value = cleaned_value.replace(',', '.')
    
    try:
        return float(cleaned_value)
    except ValueError:
        return None

if __name__ == '__main__':
    # Exemplo de uso
    print("--- Teste clean_text ---")
    sample_dirty_text = "  Este é um   texto\ncom\nmuitos  espaços e\tquebras de linha.  "
    cleaned = clean_text(sample_dirty_text)
    print(f"Original: '{sample_dirty_text}'")
    print(f"Limpo:    '{cleaned}'")

    print("\n--- Teste normalize_value ---")
    values_to_test = [
        "R$ 1.234,56",
        "1.000,00",
        "50,25",
        "1234.56", # Padrão americano
        "R$ 500",
        "abc",
        None
    ]
    for val in values_to_test:
        normalized = normalize_value(val)
        print(f"Original: '{val}' -> Normalizado: {normalized}")