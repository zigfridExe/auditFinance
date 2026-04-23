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
        text_lower = text.lower()
        for doc_type, config in self.patterns.items():
            if "identificadores" in config:
                for identifier in config["identificadores"]:
                    if identifier.lower() in text_lower:
                        return doc_type
        return "generico"

    def extract(self, text: str, doc_type: str = None) -> dict:
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
                        extracted_data[field] = match.group(1).strip()
                        break
        
        # Categorização baseada em palavras-chave no texto ou na descrição extraída
        text_for_category = text.lower()
        if "categoria" in config:
            for cat_name, keywords in config["categoria"].items():
                if any(keyword.lower() in text_for_category for keyword in keywords):
                    extracted_data["categoria"] = cat_name
                    break
                    
        return extracted_data
