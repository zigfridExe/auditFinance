# Módulo: Minerador de Contas

## Escopo
Este módulo é responsável por extrair, catalogar e consolidar dados financeiros de prestações de contas em formato PDF. Ele lê o PDF principal, identifica anexos, baixa-os, processa o texto para extrair dados estruturados (Data, Valor, Categoria, etc.) usando expressões regulares configuráveis, e gera um arquivo CSV consolidado e um relatório de inconsistências (auditoria).

**O que este módulo FAZ:**
- Lê PDFs de prestação de contas.
- Extrai links e baixa PDFs anexos.
- Classifica documentos (Ex: Conta de Luz, Recibo).
- Minera dados financeiros com base em `patterns.json`.
- Consolida dados extraídos em um arquivo CSV.
- Aponta inconsistências (falta de comprovantes ou divergência de valores).

**O que este módulo NÃO FAZ:**
- Não gerencia a autenticação de usuários.
- Não exibe os dados em uma interface gráfica (isso é papel do frontend/PowerBI).
- Não persiste os dados diretamente no banco de dados Supabase na sua primeira versão (apenas gera CSV para ingestão posterior).

## Arquitetura Interna
- `main.py`: Orquestrador principal.
- `pdf_processor.py`: Leitura de PDFs e download de anexos.
- `data_extractor.py`: Motor de regex e classificação.
- `csv_generator.py`: Geração do CSV consolidado.
- `utils.py`: Funções utilitárias de formatação e limpeza.
- `config/patterns.json`: Dicionário de regras de extração.

## Endpoints / Execução
Atualmente, o módulo é executado via script no terminal (batch processing), não possuindo endpoints HTTP expostos na versão 1.0. 
- **Comando:** `python -m mineradorDeContas.main`

*(Futuro: Será transformado em worker ou exposto via FastAPI hospedado no Render).*

## Schemas (Entrada e Saída)
Apesar de ser um script, os dados seguem um contrato estrito para a geração do CSV e ingestão futura no banco.

**Output (Linha do CSV):**
```json
{
  "data": "string (ISO-8601, ex: 2026-02-15)",
  "descricao": "string",
  "valor": "float",
  "categoria": "string",
  "documento_referencia": "string | null",
  "tipo_documento": "string",
  "origem_pdf": "string"
}
```
