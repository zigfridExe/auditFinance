# Épico 1: Fundações e Planejamento Arquitetural

**Objetivo:** Garantir que todo o alicerce do projeto (ambiente, testes e estrutura) esteja 100% definido antes de escrever a primeira linha de lógica de negócio. Sem "fazimento" às cegas.

## História 1.1: Setup do Ambiente de Desenvolvimento
**Descrição:** Como desenvolvedor, quero que os ambientes de Backend (Python) e Frontend (React/Vite) estejam configurados com suas dependências base isoladas (`requirements.txt` e `package.json`) para garantir que o código rode perfeitamente em qualquer máquina.
**Critérios de Aceite:**
- Criação do `requirements.txt` e virtualenv para o backend (API FastAPI).
- Inicialização do `package.json` para o frontend (React/Vite).
- Configuração do linter e formatadores de código (Black para Python, Prettier para JS).

## História 1.2: Infraestrutura de Testes (TDD)
**Descrição:** Como arquiteto do sistema, quero que todo o ecossistema de testes automatizados esteja configurado antes do código de produção, seguindo rigorosamente o fluxo RED-GREEN-REFACTOR.
**Critérios de Aceite:**
- Configuração do `pytest` para a API Python.
- Configuração do `Vitest`/`Testing Library` para o Frontend React.
- Esboço dos arquivos de testes para cada módulo previsto (ex: `test_pdf_processor.py`), inicialmente falhando (RED).

## História 1.3: Estruturação de Pastas e Padrões
**Descrição:** Como desenvolvedor, quero estabelecer a árvore de diretórios oficial do repositório para evitar código espalhado e garantir a modularização exigida na Regra #8.
**Critérios de Aceite:**
- Criação dos diretórios `/backend`, `/frontend`, `/doc`, `/scripts`.
- Isolamento do módulo `mineradorDeContas` dentro da arquitetura do backend.
- Estrutura base das APIs e Rotas do Frontend criadas (arquivos vazios ou mocks).

## História 1.4: Definição de Contratos de API (Mocks)
**Descrição:** Como integrador de sistemas, quero definir exatamente como o Frontend vai falar com o Backend (JSON payloads) para que ambos os lados possam ser desenvolvidos paralelamente.
**Critérios de Aceite:**
- Documentar o schema de Request (Upload do PDF).
- Documentar o schema de Response (JSON estruturado com as contas mineradas e os alertas de inconsistência).
