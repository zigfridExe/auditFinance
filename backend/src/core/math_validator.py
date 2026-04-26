"""
Mathematical Validator using Pandas
Validação de integridade financeira e prova matemática
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class MathValidator:
    def __init__(self):
        """Inicializa validador matemático"""
        pass

    def clean_value(self, value: Any) -> Optional[float]:
        """
        Limpa e converte valor para float
        
        Args:
            value: Valor (pode ser string, float, int, etc)
            
        Returns:
            Float limpo ou None se inválido
        """
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove caracteres não numéricos exceto ponto e vírgula
            cleaned = re.sub(r'[^\d.,-]', '', value)
            
            # Substitui vírgula por ponto se for separador decimal
            if ',' in cleaned and '.' in cleaned:
                # Tem ambos, assume que vírgula é milhar e ponto é decimal
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # Apenas vírgula, assume decimal
                cleaned = cleaned.replace(',', '.')
            
            try:
                return float(cleaned)
            except ValueError:
                return None
        
        return None

    def validate_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados de um documento individual
        
        Args:
            data: Dados do documento
            
        Returns:
            Dicionário com validação e anomalias detectadas
        """
        validation = {
            "valid": True,
            "anomalies": [],
            "warnings": []
        }
        
        # Valida valor
        valor = self.clean_value(data.get('valor'))
        if valor is None:
            validation["valid"] = False
            validation["anomalies"].append("Valor inválido ou não encontrado")
        elif valor <= 0:
            validation["warnings"].append("Valor é zero ou negativo")
        elif valor > 1000000:  # 1 milhão
            validation["warnings"].append("Valor muito alto (possível erro)")
        
        # Valida data
        data_str = data.get('data')
        if data_str:
            try:
                from datetime import datetime
                # Tenta diferentes formatos
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        datetime.strptime(data_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    validation["warnings"].append("Data em formato não reconhecido")
            except Exception:
                validation["warnings"].append("Data inválida")
        else:
            validation["warnings"].append("Data não encontrada")
        
        # Valida categoria
        categoria = data.get('categoria')
        if not categoria or categoria == 'Erro':
            validation["warnings"].append("Categoria não identificada")
        
        return validation

    def validate_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida um lote de documentos usando Pandas
        
        Args:
            documents: Lista de documentos
            
        Returns:
            Dicionário com validação do lote
        """
        if not documents:
            return {
                "valid": True,
                "total_documents": 0,
                "total_value": 0,
                "anomalies": [],
                "statistics": {}
            }
        
        # Cria DataFrame
        df = pd.DataFrame(documents)
        
        # Limpa valores
        df['valor_clean'] = df['valor'].apply(self.clean_value)
        
        validation = {
            "valid": True,
            "total_documents": len(documents),
            "total_value": df['valor_clean'].sum(),
            "anomalies": [],
            "statistics": {}
        }
        
        # Estatísticas
        valid_values = df['valor_clean'].dropna()
        if len(valid_values) > 0:
            validation["statistics"] = {
                "mean": float(valid_values.mean()),
                "median": float(valid_values.median()),
                "std": float(valid_values.std()),
                "min": float(valid_values.min()),
                "max": float(valid_values.max()),
                "count": len(valid_values)
            }
            
            # Detecta outliers (valores > 3 desvios padrão da média)
            mean = valid_values.mean()
            std = valid_values.std()
            if std > 0:
                outliers = valid_values[(valid_values < mean - 3*std) | (valid_values > mean + 3*std)]
                if len(outliers) > 0:
                    validation["anomalies"].append(
                        f"Detectados {len(outliers)} outliers estatísticos"
                    )
        
        # Valida documentos individuais
        for idx, doc in documents.items() if isinstance(documents, dict) else enumerate(documents):
            doc_validation = self.validate_document(doc)
            if not doc_validation["valid"]:
                validation["valid"] = False
                validation["anomalies"].extend(doc_validation["anomalies"])
            validation["warnings"] = validation.get("warnings", []) + doc_validation.get("warnings", [])
        
        return validation

    def cross_validate(self, main_doc: Dict[str, Any], attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validação cruzada entre documento principal e anexos
        
        Args:
            main_doc: Documento principal
            attachments: Lista de anexos
            
        Returns:
            Inconsistências detectadas
        """
        inconsistencies = []
        
        main_valor = self.clean_value(main_doc.get('valor'))
        
        if main_valor is not None and attachments:
            # Soma dos valores dos anexos
            attachment_values = []
            for att in attachments:
                att_valor = self.clean_value(att.get('valor'))
                if att_valor is not None:
                    attachment_values.append(att_valor)
            
            if attachment_values:
                total_attachments = sum(attachment_values)
                diff = abs(main_valor - total_attachments)
                
                # Tolerância de 1% ou R$ 10,00
                tolerance = max(main_valor * 0.01, 10.0)
                
                if diff > tolerance:
                    inconsistencies.append({
                        "type": "value_mismatch",
                        "description": f"Valor principal (R$ {main_valor:.2f}) difere da soma dos anexos (R$ {total_attachments:.2f})",
                        "severity": "high",
                        "main_value": main_valor,
                        "attachments_sum": total_attachments,
                        "difference": diff
                    })
        
        # Valida datas
        main_data = main_doc.get('data')
        if main_data and attachments:
            for att in attachments:
                att_data = att.get('data')
                if att_data and att_data != main_data:
                    inconsistencies.append({
                        "type": "date_mismatch",
                        "description": f"Data do anexo ({att_data}) difere do documento principal ({main_data})",
                        "severity": "low",
                        "attachment_filename": att.get('nome_arquivo')
                    })
        
        return inconsistencies
