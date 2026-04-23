# MVP: Plataforma de Mineração de Contas

## 1. Escopo e Objetivo do MVP
O objetivo deste Produto Mínimo Viável (MVP) é focar na entrega de valor rápido com prazo apertado ("correria"). O escopo será restrito a dois pilares fundamentais, deixando integrações complexas de IA e n8n para a Fase 2.

**Foco Total:**
1. Motor de Mineração Automática (Backend Python).
2. Interface de Operação Humana (Frontend React/Vite).

---

## 2. Pilares do MVP

### Pilar 1: Motor de Mineração (Backend)
- **Tecnologia:** Python + FastAPI.
- **Responsabilidades:**
  - Receber o upload do PDF principal (Prestação de Contas).
  - Executar o algoritmo de extração de links (Regex).
  - Fazer download automático dos anexos (notas e comprovantes).
  - Ler e processar o texto, classificando e estruturando os dados baseados no `patterns.json`.
  - Cruzar os dados para gerar o **Relatório de Inconsistências (RF11)**.
  - Retornar os dados consolidados (JSON ou link para CSV) para o Frontend.
- **Hospedagem:** Render.

### Pilar 2: Interface Humana (Frontend)
- **Tecnologia:** React (Vite) com Tailwind CSS (A estética deve ser premium, conforme padrões do Antigravity).
- **Responsabilidades:**
  - **Dashboard Simplificado:** Interface limpa e responsiva para que o síndico/usuário faça o upload do PDF.
  - **Feedback em Tempo Real:** Indicador de progresso ("Extraindo dados...", "Baixando 5 anexos...", "Minerando valores...").
  - **Tabela de Resultados:** Exibição imediata dos dados extraídos na tela.
  - **Alertas Visuais:** Destacar inconsistências na tela (ex: linha vermelha se o valor da nota diferir do balanço).
  - **Exportação:** Botão para baixar o `.csv` gerado para uso no PowerBI.
- **Hospedagem:** Vercel.

---

## 3. O Que Fica de Fora do MVP (Backlog / V2)
Para garantir a velocidade de entrega, os seguintes itens não entrarão no MVP:
- Integração com n8n.
- Chatbots ou consultas em linguagem natural (LLM).
- Visão computacional para imagens que não são PDFs de texto.
- Persistência definitiva no banco de dados Supabase (no MVP, o fluxo será processar na memória e devolver o CSV. Banco será plugado depois).

---

4. **Fases de Execução (Metodologia Antigravity)**

1. **Setup Inicial (Fase 1):**
   - Inicializar repositório React (Vite) para o Frontend.
   - Inicializar ambiente Python para o Backend (Virtualenv).
2. **Desenvolvimento do Motor Python (Fase 2 - Core):**
   - Refatorar/Desenvolver os scripts do `mineradorDeContas` em Python.
   - Criar o endpoint da API `POST /api/mine` usando FastAPI.
3. **Desenvolvimento da Interface (Fase 3):**
   - Criar página de Upload.
   - Consumir a API FastAPI.
   - Criar a tabela de visualização de resultados e inconsistências.
4. **Deploy e Teste Integrado (Fase 4):**
   - Backend na Render. Frontend na Vercel. Teste End-to-End com PDFs reais.
