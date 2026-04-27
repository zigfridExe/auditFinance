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
        # Itera na ordem do JSON (Impostos, Luz, etc primeiro)
        for doc_type, config in self.patterns.items():
            if doc_type == "generico": continue
            
            if "identificadores" in config:
                for identifier in config["identificadores"]:
                    # Se o identificador for um regex (contém \b ou []), usa busca regex
                    if "\\" in identifier or "[" in identifier:
                        if re.search(identifier, text, re.IGNORECASE):
                            return doc_type
                    # Caso contrário, busca simples para performance
                    elif identifier.lower() in text_lower:
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
        # IMPORTANTE: re.DOTALL permite que o '.' pegue quebras de linha (crucial para CPFL/Itaú)
        for field in ["data", "valor", "descricao"]:
            if field in config:
                for pattern in config[field]:
                    # Usamos DOTALL para capturar valores em linhas subsequentes ao rótulo
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        val = match.group(1).strip()
                        
                        if field == "valor":
                            # Limpeza básica de caracteres comuns que quebram o float
                            val = val.replace(" ", "")
                            # Remove pontuações finais
                            val = val.rstrip(".,; ")
                            
                            # Filtro anti-código de barras
                            numerics_only = re.sub(r'[^\d]', '', val)
                            if len(numerics_only) > 12: 
                                continue 
                            
                            try:
                                clean_val = val.replace("R$", "").strip()
                                # Se tiver ponto e virgula (BR)
                                if "," in clean_val and "." in clean_val:
                                    # Se a virgula vier depois do ponto, é BR
                                    if clean_val.rfind(",") > clean_val.rfind("."):
                                        clean_val = clean_val.replace(".", "").replace(",", ".")
                                    else: # Formato Americano
                                        clean_val = clean_val.replace(",", "")
                                elif "," in clean_val: # Apenas virgula
                                    clean_val = clean_val.replace(",", ".")
                                
                                float_val = float(clean_val)
                                val = f"{float_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            except:
                                pass 
                                
                        extracted_data[field] = val
                        break
        
        # Categorização baseada em palavras-chave
        text_for_category = text.lower()
        if "categoria" in config:
            for cat_name, keywords in config["categoria"].items():
                if any(keyword.lower() in text_for_category for keyword in keywords):
                    extracted_data["categoria"] = cat_name
                    break
                    
        return extracted_data
