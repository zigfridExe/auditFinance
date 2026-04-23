class AuditEngine:
    def __init__(self):
        pass

    def audit(self, main_doc_data: dict, attachments_data: list[dict]) -> list[dict]:
        """
        Cruza os dados do documento principal com os dados dos anexos.
        Retorna uma lista de inconsistências.
        """
        inconsistencies = []
        
        # Lógica super simples pro MVP: Verifica se o total do principal 
        # bate com a soma dos anexos (apenas se todos tiverem valor)
        
        if not main_doc_data.get("valor"):
            return inconsistencies
            
        try:
            main_total = float(main_doc_data["valor"].replace(".", "").replace(",", "."))
            
            attachments_total = 0.0
            for att in attachments_data:
                if att.get("valor"):
                    val = float(att["valor"].replace(".", "").replace(",", "."))
                    attachments_total += val
            
            # Se tiver anexos, mas a soma não bate
            if len(attachments_data) > 0 and abs(main_total - attachments_total) > 0.01:
                inconsistencies.append({
                    "tipo": "DIVERGENCIA_VALOR",
                    "mensagem": f"Valor total da prestação (R$ {main_total}) difere da soma dos comprovantes (R$ {attachments_total})",
                    "severidade": "ALTA"
                })
        except Exception as e:
            inconsistencies.append({
                "tipo": "ERRO_CONVERSAO",
                "mensagem": f"Falha ao calcular divergência: {str(e)}",
                "severidade": "BAIXA"
            })
            
        return inconsistencies
