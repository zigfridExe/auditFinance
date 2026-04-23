# Projeto: Mineração de Dados de Prestação de Contas de Condomínio

## Objetivo

Automatizar a extração de dados financeiros de PDFs de prestação de contas de condomínio e seus documentos anexos (via links), consolidando-os em um formato CSV. Os dados minerados serão utilizados para a criação de dashboards no Power BI e uma interface web dinâmica para análise.

## Desafios

*   **Variedade de Layouts de PDF:** Documentos de diferentes fornecedores (contas de consumo, notas fiscais, recibos) possuem layouts distintos, exigindo abordagens flexíveis para a extração de dados.
*   **Extração de Links:** Identificar e baixar corretamente os PDFs referenciados por links dentro do documento principal.
*   **Consolidação de Dados:** Padronizar e unificar informações de diversas fontes em um único CSV.

## Visão de Futuro (Product Roadmap)

O objetivo final não é apenas extrair dados, mas criar um ecossistema de inteligência para o condomínio:
1.  **Processamento Bruto (Python):** Mineração, catalogação e relacionamento de gastos.
2.  **Dashboards Dinâmicos:** Visualização clara para tomada de decisão.
3.  **Inteligência Artificial (n8n/AI):** Integração com ferramentas de automação (n8n) e LLMs para permitir consultas em linguagem natural (ex: "Puxa a capivara desse fornecedor X na contabilidade").
4.  **Auditoria Automatizada:** Identificação proativa de padrões suspeitos, cobranças duplicadas ou variações anômalas de preço.
5.  **Visão Computacional:** Uso de IA Multimodal para analisar fotos de comprovantes físicos, manutenções (ex: fotos de peças de elevador) e notas fiscais digitalizadas.

## Stack Tecnológica Alvo (Consolidada)

A stack oficial do projeto, sem invenções ou "pó de chifre de unicórnio", é:

*   **Frontend:** React (usando Vite, sem Next.js) para a interface do usuário.
*   **Backend:** Node.js (API REST estruturada para o processamento de arquivos e auditoria).
*   **Banco de Dados:** PostgreSQL bruto (sem ORM como Prisma, SQL nativo na veia).
*   **Armazenamento de Arquivos:** Sistema de arquivos local para o MVP (pasta `archives` ou similar) com evolução futura para storage em nuvem caso necessário.

## Plano de Ação Detalhado

### 1. Estrutura do Projeto

Será criada uma árvore de diretórios focada em Node.js e React puro, separando Frontend e Backend:

```
c:/manutencao/auditFinance/
├── backend/                    # API em Node.js
│   ├── src/
│   │   ├── controllers/
│   │   ├── services/           # Lógica de mineração e extração de PDF
│   │   ├── db/                 # Conexão e queries SQL bruto
│   │   ├── utils/
│   │   └── index.js
│   ├── config/
│   │   └── patterns.json       # Arquivo JSON com os padrões de regex
│   ├── archives/               # Pasta persistente para os PDFs originais (não apagar)
│   └── package.json
├── frontend/                   # Interface em React puro (Vite)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── doc/                        # Documentação e regras de negócio
```

### 2. Tecnologias e Bibliotecas (Ecosistema Node)

*   **Leitura de PDF e Extração de Texto/Links:** `pdf-parse` (ou `pdfjs-dist`).
*   **Download de Arquivos:** `axios` ou fetch nativo do Node.
*   **Extração de Dados Estruturados:** Regex nativo do JavaScript.
*   **Geração de CSV:** `fast-csv` ou lógica manual.
*   **Banco de Dados:** `pg` (node-postgres) para executar queries cruas.

### 3. Instalação das Dependências (Backend)

O ambiente será inicializado via `npm` no diretório `/backend`.

### 4. Lógica de Mineração (Migração para Node.js)

Todo o core de processamento de texto e geração de CSV será reimplementado em JavaScript (`Node.js`), garantindo que o backend extraia os PDFs e devolva as respostas na API REST. A estrutura lógica do `patterns.json` continuará a mesma para separar as regras de Regex do código.

### 6. Configuração dos Padrões de Extração (`mineradorDeContas/config/patterns.json`)

O arquivo `patterns.json` é crucial para a extração de dados. Ele define as expressões regulares e palavras-chave que o `DataExtractor` usará para encontrar informações nos PDFs.

**Estrutura:**

```json
{
    "generico": {
        "data": ["(\\d{2}/\\d{2}/\\d{4})", "(\\d{2} de [a-zA-Z]+ de \\d{4})"],
        "valor": ["Total:\\s*([\\d\\.,]+)", "R\\$\\s*([\\d\\.,]+)"],
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
        "valor": ["Valor a Pagar\\s*R\\$\\s*([\\d\\.,]+)"],
        "descricao": ["Consumo de Energia Elétrica"],
        "categoria": { "Luz": ["energia", "eletricidade"] }
    }
    // Adicione mais tipos de documentos aqui (ex: "conta_agua", "nota_fiscal", "recibo_salario")
    // Para cada tipo, defina:
    // "identificadores": Lista de regex ou palavras-chave para classificar o documento.
    // "data": Lista de regex para extrair a data.
    // "valor": Lista de regex para extrair o valor.
    // "descricao": Lista de regex para extrair a descrição.
    // "categoria": Dicionário onde a chave é a categoria e o valor é uma lista de palavras-chave para identificá-la.
    // "documento_referencia": Lista de regex para extrair números de documentos.
}
```
```