# Lições Aprendidas (Desenvolvimento Assistido por IA)

> *Este documento visa catalogar as armadilhas e as melhores estratégias empíricas descobertas durante a construção do software com Inteligência Artificial.*

---

## 1. O Paradigma "Anti-Framework" com IA
**A Constatação:** Usar frameworks complexos e bibliotecas pesadas de terceiros (ex: `react-use-websocket`, `Pandas`, `Prisma`) com IA é uma bomba-relógio.
**O Motivo:** A IA alucina integrações de versões antigas com versões novas (ESM vs CommonJS), gera conflitos de compilação em diferentes sistemas operacionais (C++ no Windows) e esconde o que está quebrado atrás de uma "caixa preta". Quando um framework quebra na mão da IA, o debug se torna um loop de tela branca difícil de resolver.

### 🛡️ A Estratégia de Defesa:
*   **Priorizar a API Nativa:** Sempre que possível, usar Vanilla JS, WebSockets nativos do navegador (`new WebSocket()`), `fetch` (ou `axios` simples). O que é construído nos motores nativos não quebra com atualizações do Node ou Vite.
*   **Zero Magic Abstractions:** Se a tarefa é manipular dados ou extrair textos, usar bibliotecas puras do Python (`csv` nativo, dicionários e listas nativas) é 100x mais confiável do que instalar um monstro como o `Pandas`.

---

## 2. Abordagem "Zero Trust" (Confiança Zero em Arquivos)
**A Constatação:** Em projetos de Automação/Mineração, a IA inicialmente tenta ler os arquivos "às cegas" (ex: forçar todo link a ser `.pdf` e tentar abrir com PyPDF). Isso causa crashes fatais como *Internal Server Error* ou travamentos no processamento.

### 🛡️ A Estratégia de Defesa (O Padrão *Strategy*):
*   **Nunca confie na extensão da URL:** Sempre force o backend a olhar os "Headers" (`Content-Type`) de uma requisição HTTP para descobrir a verdadeira natureza do arquivo.
*   **Bifurcação de Decisão:** O programa deve checar a extensão antes de escolher a ferramenta:
    *   `.pdf` -> `PyPDF`
    *   `.jpg` -> `Tesseract OCR`
    *   `Desconhecido` -> Trata exceção (Fail Fast) e registra no log em vez de travar o motor.
*   **Isolamento (Try/Catch em Loop):** Falhas em itens individuais de uma lista (como o download de um anexo) nunca devem quebrar a esteira principal. Eles viram status de "Erro" visível pro usuário.

---

## 3. Ambientes e Bloqueios de Segurança na Nuvem
**A Constatação:** Ao baixar documentos da AWS, Superlógica ou Drive, os robôs base de Python e Node tomam "Erro 403 / Access Denied" porque servidores modernos usam Cloudflare ou firewalls que barram bibliotecas com User-Agents genéricos (ex: `python-requests/2.31`).

### 🛡️ A Estratégia de Defesa:
*   Sempre mascare os scrapers e crawlers da aplicação colocando um `User-Agent` de navegadores reais (ex: Chrome no Windows 11).

## 4. Arquitetura Orientada a Dados (Data-Driven) para Mineração (O "patterns.json")
**A Constatação:** Tentar fazer IFs e ELIFs gigantescos no código Python/Node para cada novo layout de documento contábil (Enel, Sabesp, DARF, Holerite) torna o código impossível de manter e propenso a quebras.

### 🛡️ A Estratégia de Defesa (O Motor Modular):
*   **A Abordagem:** Separamos o "Músculo" do "Cérebro". O código Python (`data_extractor.py`) tem apenas a lógica de extração genérica (aplicar Regex). Todo o conhecimento de como ler um documento fica em um arquivo de texto simples (`patterns.json`).
*   **Vantagens:** 
    *   **Atualização a Quente:** Se o governo lança uma guia nova amanhã, você não precisa recompilar ou alterar o código da aplicação. Você apenas edita o `patterns.json`.
    *   **Escalabilidade Perfeita:** Em 10 minutos mapeamos Notas Fiscais (NFS-e, DANFE), Boletos, Folhas de Pagamento e Guias de ISS apenas criando blocos JSON, tornando a ferramenta útil para meses passados (onde a estrutura do documento é a mesma) de forma instantânea.
    *   **Não Alucina:** Diferente do uso irrestrito de LLMs para extração contábil (que é caro e perigoso), o Regex determinístico tira os números exatos. Apenas usamos a IA (Gemini) para **escrever o Regex** do JSON e não para **processar o PDF** diretamente.

---

*(Documento vivo: Adicionar novas descobertas conforme o avanço do projeto).*
