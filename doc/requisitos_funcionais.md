# Requisitos Funcionais - Projeto Minerador de Contas

Este documento detalha as funcionalidades que o sistema de mineração de dados de prestação de contas de condomínio deve possuir para atingir seu objetivo.

## 1. Introdução

O objetivo deste projeto é automatizar a extração de dados financeiros de documentos de prestação de contas (PDFs) e consolidá-los em um formato CSV para análise posterior em ferramentas como Power BI.

---

## 2. Requisitos Funcionais (RF)

| ID | Nome | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| **RF01** | **Extração de Texto** | O sistema deve extrair o texto bruto de arquivos PDF de forma integral. | Alta |
| **RF02** | **Identificação de Links** | O sistema deve localizar metadados de links (URIs) no PDF principal que referenciam outros documentos PDF. | Alta |
| **RF03** | **Download e Armazenamento** | O sistema deve baixar os PDFs apontados pelos links e armazená-los em um diretório persistente (físico ou via bucket/storage) para permitir a consulta futura do documento original. | Alta |
| **RF04** | **Classificação de Documentos** | O sistema deve classificar automaticamente o tipo de documento (ex: Conta de Luz, Água, Recibo, Nota Fiscal) baseando-se em palavras-chave e padrões de texto. | Média |
| **RF05** | **Extração de Dados Financeiros** | O sistema deve minerar campos específicos: **Data**, **Descrição**, **Valor**, **Categoria** e **Documento de Referência**. | Alta |
| **RF06** | **Configuração Flexível (Regex)** | O sistema deve utilizar um arquivo de configuração externo (`patterns.json`) para definir as expressões regulares de extração, permitindo ajustes sem alterar o código. | Alta |
| **RF07** | **Normalização de Dados** | Valores monetários (ex: "R$ 1.234,56") e datas devem ser convertidos para formatos padronizados (Float e ISO-8601). | Alta |
| **RF08** | **Consolidação em CSV** | O sistema deve gerar um único arquivo CSV contendo os dados de todos os documentos processados no lote. | Alta |
| **RF09** | **Rastreabilidade de Origem** | Cada linha do CSV resultante deve conter o nome do arquivo PDF de origem do dado. | Média |
| **RF10** | **Retenção de Arquivos (Archive)** | O sistema deve manter os comprovantes em pastas organizadas (ex: por mês/ano) ou gerar links permanentes no CSV para que as notas possam ser auditadas manualmente a qualquer momento. | Alta |
| **RF11** | **Relatório de Inconsistências** | O sistema deve comparar os lançamentos listados no PDF principal com os documentos anexos processados. Caso um lançamento não possua comprovação ou o valor divirja, deve ser gerado um relatório de alertas. | Alta |

---

## 3. Requisitos Não Funcionais (RNF)

| ID | Nome | Descrição |
| :--- | :--- | :--- |
| **RNF01** | **Tecnologia** | O sistema deve ser desenvolvido em Python no backend (utilizando `FastAPI`, `PyPDF2`, `pandas`) e React puro (Vite) no frontend, consumindo um PostgreSQL via queries cruas (sem ORM). |
| **RNF02** | **Tratamento de Erros** | Falhas em downloads individuais ou PDFs ilegíveis não devem travar a execução do programa principal. |
| **RNF03** | **Manutenibilidade** | A lógica de extração deve ser modularizada para facilitar a adição de novos layouts de PDF. |
| **RNF04** | **Codificação** | O arquivo CSV gerado deve utilizar codificação UTF-8 para garantir a integridade de caracteres especiais. |

---

## 4. Fluxo de Operação Sugerido

1.  **Input:** O usuário fornece o caminho do PDF de prestação de contas principal.
2.  **Processamento Inicial:** O sistema extrai dados do PDF principal e identifica links para anexos.
3.  **Captura de Anexos:** O sistema baixa os anexos.
4.  **Mineração:** O sistema processa cada anexo, classifica e extrai os dados financeiros.
5.  **Output:** O sistema gera o CSV consolidado com links de referência e o relatório de inconsistências (se houver), garantindo que os PDFs originais permaneçam salvos para auditoria.
