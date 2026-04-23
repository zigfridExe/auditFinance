# Épico 2: O Motor de Mineração (Backend Python)

**Objetivo:** Implementar a lógica bruta de extração, processamento e auditoria (RF11) garantindo que a API retorne dados perfeitamente estruturados. Tudo guiado pelos testes criados no Épico 1.

## História 2.1: Processamento Base de PDFs e Links
**Descrição:** Como sistema, preciso ler o arquivo principal (via `PyPDF2` ou `pdfplumber`), extrair o texto bruto e localizar os links para download dos comprovantes anexos.

## História 2.2: Download e Retenção de Documentos
**Descrição:** Como sistema, preciso baixar os arquivos anexos de forma assíncrona/segura para uma pasta estruturada (ex: por mês/ano) e manter esses arquivos persistidos para futura consulta de auditoria (não apagar).

## História 2.3: Extrator Inteligente (Regex & Classificação)
**Descrição:** Como motor de extração, devo usar o `patterns.json` para classificar o que é cada PDF e garimpar Data, Valor, Descrição e Documento de Referência usando Regex puro (`re`) do Python.

## História 2.4: Módulo de Auditoria (Inconsistências)
**Descrição:** Como auditor financeiro automatizado, cruzarei os dados do PDF principal com os anexos minerados para disparar a lista de falhas ou divergências de valor, preparando os dados para a interface.

## História 2.5: Exposição via API
**Descrição:** Como desenvolvedor, preciso expor todo esse motor através de um endpoint seguro (REST) usando **FastAPI** para que a interface React consiga acioná-lo localmente.
