# Arquitetura Híbrida de Auditoria Financeira

## Visão Geral

Pipeline inteligente que detecta automaticamente o tipo de PDF e escolhe o método de extração mais adequado.

## Pipeline

```
PDF → Detector de Tipo → [Digital] → pypdf + Regex → SQLite
                     → [Escaneado] → PaddleOCR → Qwen2.5-0.5B → Regex/Pandas → SQLite
```

## Componentes

### 1. Detector de Tipo de PDF (`pdf_type_detector.py`)
- Detecta se PDF é digital (texto selecionável) ou escaneado (imagem)
- Usa heurística baseada em quantidade de texto extraível
- Threshold configurável (padrão: 100 caracteres)

### 2. OCR Processor (`ocr_processor.py`)
- Usa PaddleOCR para extrair texto de PDFs escaneados
- Converte PDF para imagens (PyMuPDF) e aplica OCR
- Suporta português
- CPU-only mode (sem GPU)

### 3. Ollama Client (`ollama_client.py`)
- Wrapper para API local do Ollama
- Modelo: Qwen2.5-0.5B (~397MB)
- Gera JSON estruturado a partir de texto bruto
- Fallback automático se Ollama não estiver disponível

### 4. Semantic Structurer (`semantic_structurer.py`)
- Usa LLM para estruturação semântica inteligente
- System prompt estrito para extração financeira
- Retorna JSON com: data, valor, descricao, categoria

### 5. Hybrid Processor (`hybrid_processor.py`)
- Orquestra todo o pipeline
- Escolhe método baseado no tipo de PDF
- Múltiplos níveis de fallback:
  - Digital: pypdf + regex
  - Escaneado: OCR → Ollama → regex → pypdf (fallback)

### 6. Database Manager (`database.py`)
- SQLite para persistência local
- Tabelas: main_documents, attachments, inconsistencies
- Zero-config, arquivo único
- Índices para performance

### 7. Math Validator (`math_validator.py`)
- Validação matemática com Pandas
- Limpeza de valores (R$, vírgulas, etc)
- Detecção de outliers estatísticos
- Validação cruzada (doc principal vs anexos)

## Instalação

### 1. Ollama (já instalado)
```bash
# Verificar se está rodando
ollama list

# Modelo já baixado
ollama pull qwen2.5:0.5b
```

### 2. Dependências Python
```bash
cd backend
pip install -r requirements.txt
```

### 3. Tesseract OCR (para imagens)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por

# Verificar instalação
tesseract --version
```

## Uso

### Exemplo básico
```python
from backend.src.core.hybrid_processor import HybridProcessor

processor = HybridProcessor()
result = processor.process("caminho/do/arquivo.pdf")

print(result)
# {
#   "data": "15/01/2026",
#   "valor": 1500.50,
#   "descricao": "Conta de Luz",
#   "categoria": "Luz",
#   "extraction_method": "digital_regex",
#   "extraction_success": True
# }
```

### Com validação matemática
```python
from backend.src.core.math_validator import MathValidator

validator = MathValidator()
validation = validator.validate_document(result)
print(validation)
```

### Com banco de dados
```python
from backend.src.core.database import DatabaseManager

db = DatabaseManager("audit_finance.db")
doc_id = db.save_main_document(result, "arquivo.pdf")
```

## Métodos de Extração

| Método | Quando usado | Velocidade | Precisão |
|--------|-------------|------------|----------|
| digital_regex | PDF digital | Muito rápido | Alta |
| scanned_ollama | PDF escaneado + Ollama disponível | Lento | Muito alta |
| scanned_ocr_regex | PDF escaneado + Ollama indisponível | Lento | Média |
| fallback_regex | Tentativa final | Rápido | Baixa |

## Fallbacks

O sistema tem múltiplos níveis de fallback:

1. **PDF Digital**: pypdf → regex
2. **PDF Escaneado**: 
   - OCR → Ollama (ideal)
   - OCR → regex (se Ollama falhar)
   - pypdf direto (último recurso)

## Performance

- PDF Digital: < 1 segundo
- PDF Escaneado (OCR): 5-30 segundos (depende do tamanho)
- Ollama: 2-5 segundos por documento

## Troubleshooting

### Ollama não disponível
- Verificar: `ollama list`
- Reiniciar serviço: `sudo systemctl restart ollama`

### PaddleOCR erro
- Verificar instalação: `pip list | grep paddle`
- Reinstalar: `pip install paddleocr paddlepaddle`

### Tesseract não encontrado
- Instalar: `sudo apt-get install tesseract-ocr tesseract-ocr-por`

## Próximos Passos

- [ ] Integrar pipeline híbrido no main.py
- [ ] Criar endpoints para consulta ao SQLite
- [ ] Adicionar frontend para visualização
- [ ] Testes com PDFs reais
