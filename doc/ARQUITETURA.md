# Arquitetura do Projeto AuditFinance

## Visão Geral

O **AuditFinance** é um sistema de mineração e auditoria de contas, projetado para processar prestações de contas em PDF, extrair dados automaticamente de anexos, e realizar auditorias cruzadas para identificar inconsistências financeiras.

### Stack Tecnológico

- **Backend**: Python 3.x + FastAPI
- **Frontend**: React 19 + Vite + TailwindCSS
- **OCR**: PaddleOCR, Tesseract, PyMuPDF
- **LLM**: Google Gemini API, Ollama (local)
- **Comunicação**: REST API + WebSocket (logs em tempo real)

---

## Estrutura de Diretórios

```
auditFinance/
├── backend/
│   ├── archives/              # Armazenamento de PDFs baixados
│   ├── src/
│   │   ├── api/              # Rotas da API
│   │   │   └── test_routes.py
│   │   ├── config/           # Configurações e patterns
│   │   │   ├── patterns.json
│   │   │   └── manual_fixes.json
│   │   ├── core/             # Módulos principais de processamento
│   │   │   ├── pdf_processor.py
│   │   │   ├── downloader.py
│   │   │   ├── audit.py
│   │   │   ├── data_extractor.py
│   │   │   ├── database.py
│   │   │   ├── gemini_client.py
│   │   │   ├── ollama_client.py
│   │   │   ├── llm_wrapper.py
│   │   │   ├── math_validator.py
│   │   │   ├── ocr_processor.py
│   │   │   ├── tesseract_ocr.py
│   │   │   ├── hybrid_processor.py
│   │   │   ├── pdf_type_detector.py
│   │   │   └── semantic_structurer.py
│   │   └── main.py           # Entry point da API
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx          # Interface principal
│   │   ├── Tests.jsx        # Interface de testes
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── doc/                      # Documentação
└── .env                     # Variáveis de ambiente
```

---

## Arquitetura do Backend

### Camadas

```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  - /api/mine (POST)                     │
│  - /api/mine_batch (POST)               │
│  - /api/mine_folder (POST)              │
│  - /api/ws/logs (WebSocket)              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Business Logic Layer (Core)        │
│  - PDFProcessor                         │
│  - DocumentDownloader                   │
│  - AuditEngine                          │
│  - HybridProcessor                      │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Data Extraction Layer             │
│  - OCR (PaddleOCR, Tesseract)          │
│  - LLM (Gemini, Ollama)                 │
│  - PDF Parsing (PyMuPDF, pdfplumber)   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Storage Layer                     │
│  - Local filesystem (archives/)         │
│  - Database (SQLite via database.py)   │
└─────────────────────────────────────────┘
```

### Módulos Core

#### 1. **PDFProcessor** (`pdf_processor.py`)
- Responsabilidade: Orquestrar o processamento de PDFs
- Funções principais:
  - `extract_links()`: Extrai links de anexos de PDFs principais
  - `extract_structured()`: Pipeline híbrido para extração de dados
- Integra: HybridProcessor, PDFTypeDetector

#### 2. **HybridProcessor** (`hybrid_processor.py`)
- Responsabilidade: Pipeline híbrido de extração (OCR + LLM)
- Estratégia:
  1. Detecta tipo do PDF (digital vs scaneado)
  2. Aplica OCR se necessário
  3. Usa LLM para estruturação semântica
  4. Valida matematicamente os valores extraídos
- Integra: PDFTypeDetector, OCRProcessor, LLMWrapper, MathValidator, SemanticStructurer

#### 3. **DocumentDownloader** (`downloader.py`)
- Responsabilidade: Download de anexos de URLs
- Features:
  - Suporte a diretório de trabalho customizável
  - Tratamento de páginas HTML de roteamento (ex: Superlógica)
  - Extração recursiva de links em HTML
- Integra: BeautifulSoup para parsing de HTML

#### 4. **AuditEngine** (`audit.py`)
- Responsabilidade: Auditoria cruzada de dados
- Validações:
  - Soma de anexos vs documento principal
  - Datas fora do período
  - Valores negativos ou suspeitos
  - Duplicatas
- Retorna: Lista de inconsistências com severidade

#### 5. **LLMWrapper** (`llm_wrapper.py`)
- Responsabilidade: Abstração para múltiplos provedores LLM
- Implementações:
  - `GeminiClient`: Google Gemini API
  - `OllamaClient`: LLM local via Ollama
- Features: Fallback automático entre provedores

#### 6. **OCRProcessor** (`ocr_processor.py`)
- Responsabilidade: Extração de texto de imagens/PDFs
- Implementações:
  - `TesseractOCR`: Tesseract OCR
  - Processamento via PaddleOCR (configurável)
- Features: Pré-processamento de imagem para melhor acurácia

#### 7. **MathValidator** (`math_validator.py`)
- Responsabilidade: Validação matemática de valores
- Funções:
  - Extração de valores monetários de texto
  - Cálculos de soma
  - Detecção de valores inconsistentes

#### 8. **SemanticStructurer** (`semantic_structurer.py`)
- Responsabilidade: Estruturação de dados extraídos
- Funções:
  - Categorização de despesas
  - Normalização de datas
  - Extração de descrições

#### 9. **PDFTypeDetector** (`pdf_type_detector.py`)
- Responsabilidade: Detectar tipo de PDF
- Tipos:
  - PDF digital (texto selecionável)
  - PDF scaneado (imagem)
  - PDF misto
- Usa: PyMuPDF para análise

#### 10. **Database** (`database.py`)
- Responsabilidade: Persistência de dados
- Features:
  - Armazenamento de extrações
  - Histórico de processamentos
  - Queries para relatórios

---

## Arquitetura do Frontend

### Componentes Principais

#### 1. **App.jsx** - Interface Principal
- **Estado**:
  - `file`: Arquivo PDF selecionado
  - `workDir`: Diretório de trabalho
  - `loading`: Estado de carregamento
  - `results`: Dados extraídos
  - `logs`: Logs do terminal (WebSocket)
- **Funcionalidades**:
  - Upload de PDF principal
  - Processamento de lote (pasta local)
  - Exportação CSV
  - Visualização de resultados em tabela
  - Terminal de logs em tempo real

#### 2. **Tests.jsx** - Interface de Testes
- Funcionalidades de teste e debug do sistema

### Comunicação com Backend

- **REST API**:
  - `POST /api/mine`: Processa PDF principal + anexos
  - `POST /api/mine_batch`: Processa lote de arquivos
  - `POST /api/mine_folder`: Processa pasta local
- **WebSocket**:
  - `ws://localhost:8000/api/ws/logs`: Logs em tempo real

### Estilização

- **Framework**: TailwindCSS 4.x
- **Ícones**: Lucide React
- **Design**: Modern, clean, responsivo
- **Paleta**: Slate (neutros) + Blue (primary) + Emerald (success) + Red (error)

---

## Fluxo de Processamento

### Fluxo Principal: Mineração de PDF

```
1. Usuário faz upload de PDF principal
   ↓
2. Backend recebe arquivo (/api/mine)
   ↓
3. PDFProcessor extrai links de anexos
   ↓
4. Para cada link:
   a. DocumentDownloader baixa o arquivo
   b. Se for HTML, extrai novos links recursivamente
   c. Se for PDF/Imagem, processa com HybridProcessor
   ↓
5. HybridProcessor:
   a. PDFTypeDetector identifica tipo
   b. OCRProcessor extrai texto (se necessário)
   c. LLMWrapper estrutura dados
   d. MathValidator valida valores
   ↓
6. AuditEngine realiza auditoria cruzada
   ↓
7. Resultado retornado ao frontend
   ↓
8. Frontend exibe tabela + inconsistências
```

### Fluxo de Processamento em Lote

```
1. Usuário seleciona pasta ou múltiplos arquivos
   ↓
2. Backend recebe (/api/mine_batch ou /api/mine_folder)
   ↓
3. Para cada arquivo:
   a. Processa com HybridProcessor
   b. Adiciona ao array de resultados
   ↓
4. AuditEngine valida lote
   ↓
5. Resultado retornado
```

---

## Configurações

### Variáveis de Ambiente (.env)

```env
GEMINI_API_KEY=chave_api_gemini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
API_HOST=0.0.0.0
API_PORT=8000
```

### Arquivos de Configuração

#### patterns.json
- Regex patterns para extração de dados
- Categorias de despesas
- Formatos de data

#### manual_fixes.json
- Correções manuais para casos específicos
- Mapeamentos de categorias

---

## Integrações Externas

### 1. Google Gemini API
- Uso: Extração estruturada de dados
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- Auth: API Key

### 2. Ollama (Local)
- Uso: LLM local (alternativa ao Gemini)
- Endpoint: `http://localhost:11434/api/generate`
- Modelos: llama3.2, mistral, etc.

### 3. Superlógica (implícito)
- Sistema de gestão de contas
- PDFs contêm links para anexos
- Páginas HTML de roteamento são parseadas

---

## Banco de Dados

### Esquema (SQLite)

**Tabela: extractions**
```sql
- id (PK)
- filename
- data (JSON)
- valor (FLOAT)
- categoria
- descricao
- source_link
- extraction_method
- created_at
```

**Tabela: audit_logs**
```sql
- id (PK)
- extraction_id (FK)
- tipo_inconsistencia
- mensagem
- severidade
- created_at
```

---

## Segurança

### CORS
- Configurado para aceitar qualquer origem (desenvolvimento)
- Produção: restringir origens específicas

### Upload
- Validação de extensão (.pdf, .jpg, .jpeg, .png)
- Sanitização de nomes de arquivo

### API Keys
- Armazenadas em .env (não commitadas)
- Carregadas via python-dotenv

---

## Performance

### Otimizações
- Processamento paralelo de anexos (async/await)
- Cache de PDFs baixados (archives/)
- WebSocket para logs não-bloqueantes
- Pipeline híbrido com fallback rápido

### Limitações
- LLM calls podem ser lentos (dependência de rede)
- OCR consome CPU intensivamente
- Grandes lotes podem causar timeout

---

## Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Produção
- Backend: Docker container recomendado
- Frontend: Build estático + Nginx
- Banco: SQLite (simples) ou PostgreSQL (escalável)

---

## Roadmap Futuro

### Curto Prazo
- [ ] Autenticação de usuários
- [ ] Histórico de processamentos
- [ ] Dashboard de métricas

### Médio Prazo
- [ ] Suporte a mais formatos (Excel, Word)
- [ ] Integração com outros sistemas (ERP)
- [ ] Exportação para múltiplos formatos (Excel, PDF)

### Longo Prazo
- [ ] ML para detecção de fraudes
- [ ] API pública para terceiros
- [ ] Multi-tenancy

---

## Troubleshooting Comum

### OCR falhando
- Verificar se Tesseract/PaddleOCR está instalado
- Verificar dependências de sistema (leptonica, etc.)

### LLM não respondendo
- Verificar API Key do Gemini
- Verificar se Ollama está rodando (localhost:11434)

### Download de anexos falhando
- Verificar conectividade com Superlógica
- Verificar se work_dir está correto

### Valores incorretos
- Ajustar patterns.json
- Adicionar manual_fixes.json para casos específicos

---

## Contato & Suporte

Para dúvidas ou problemas, consulte:
- Documentação em `doc/`
- Logs do terminal na interface
- Logs do backend (stdout)
