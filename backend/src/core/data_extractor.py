import json
import re
import os

class DataExtractor:
    def __init__(self, patterns_path: str = None):
        if not patterns_path:
            # Default path to patterns.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            patterns_path = os.path.join(base_dir, "config", "patterns.json")
        
        with open(patterns_path, "r", encoding="utf-8") as f:
            self.patterns = json.load(f)

    def classify(self, text: str) -> str:
        if not text:
            return "generico"
            
        text_lower = text.lower()
        for doc_type, config in self.patterns.items():
            if "identificadores" in config:
                for identifier in config["identificadores"]:
                    if identifier.lower() in text_lower:
                        return doc_type
        return "generico"

    def extract(self, text: str, doc_type: str = None) -> dict:
        if not text:
            return {
                "data": None,
                "valor": None,
                "descricao": None,
                "categoria": "Erro"
            }
            
        if not doc_type:
            doc_type = self.classify(text)
            
        config = self.patterns.get(doc_type, self.patterns.get("generico"))
        
        extracted_data = {
            "data": None,
            "valor": None,
            "descricao": None,
            "categoria": "Outros"
        }

        # Extração de dados usando os padrões regex
        for field in ["data", "valor", "descricao"]:
            if field in config:
                for pattern in config[field]:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        val = match.group(1).strip()
                        
                        if field == "valor":
                            # Remove pontuações finais
                            val = val.rstrip("., ")
                            
                            # Filtro anti-código de barras (se tiver mais de 15 números seguidos ou pontuações estranhas, ignora)
                            # Remove tudo exceto numeros e virgula/ponto para contar
                            numerics_only = re.sub(r'[^\d]', '', val)
                            if len(numerics_only) > 12: # Um valor com mais de 12 dígitos é na casa dos Bilhões (improvável) ou é código de barras
                                continue 
                            
                            # Tenta formatar para o padrão brasileiro garantido
                            # Ex: 1.500.20 ou 1,500.20 ou 1500,20
                            # Se tiver ponto e virgula, a virgula costuma ser o decimal no BR
                            try:
                                clean_val = val.replace("R$", "").strip()
                                # Se estiver no formato americano (1,000.00)
                                if re.match(r'^\d{1,3}(,\d{3})*\.\d{2}$', clean_val):
                                    clean_val = clean_val.replace(",", "")
                                # Formato brasileiro (1.000,00)
                                else:
                                    clean_val = clean_val.replace(".", "").replace(",", ".")
                                
                                float_val = float(clean_val)
                                val = f"{float_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            except:
                                pass # Mantém o original se der erro
                                
                        extracted_data[field] = val
                        break
        
        # Categorização baseada em palavras-chave no texto ou na descrição extraída
        text_for_category = text.lower()
        if "categoria" in config:
            for cat_name, keywords in config["categoria"].items():
                if any(keyword.lower() in text_for_category for keyword in keywords):
                    extracted_data["categoria"] = cat_name
                    break
                    
        return extracted_data
