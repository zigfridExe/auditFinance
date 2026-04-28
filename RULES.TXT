# Diretrizes para Agentes de Desenvolvimento IA - ReportÁgua V2

Para manter o profissionalismo, a integridade da marca e a rastreabilidade segura do projeto, todos os agentes de IA operando nesta codebase DEVEM seguir estas regras estritamente:

## 0. Regras de Negócio
- NUNCA JAMAIS EM IPOTESE ALGUMA EXIBA OS VALORES DAS CHAVES DAS VARIAVEIS DO .ENV EM LUGAR NEM UM O UNICO TIPO DE ACESSO DEVE SER VIA CÓDIGO SCRIPT NA PROPRIA APLICAÇÃO E NUNCA NUNCA NUNCA NA CONVERSA COM O USUÁRIO.
- **Segurança Zero Trust (Confiança Zero):** NUNCA confie, SEMPRE verifique. Nenhum input de usuário, requisição de frontend ou chamada de API deve ser considerado seguro por padrão. Tudo deve ser sanitizado, autenticado, autorizado (RBAC) e validado rigorosamente antes de bater no banco de dados. Privilégio mínimo sempre.

## 1. Neutralidade de Identidade
- **PROIBIDO** o uso de personas fictícias, apelidos (ex: Khipukamaiuq, Viking, Oráculo) ou histórias de fundo em comentários, logs, documentação ou interfaces.
- Toda comunicação deve ser técnica, profissional e neutra em português brasileiro.

## 2. Autoria e Git
- **PROIBIDO** alterar a identidade do autor nos commits sem autorização expressa.
- Os commits devem sempre utilizar o e-mail e nome oficiais do proprietário do repositório:
  - **Nome:** Everton Lyons Romansini
  - **Email:** zigfrid.exe@gmail.com

## 3. Integridade do Código
- Comentários no código devem focar UNICAMENTE no "porquê" (lógica de negócio) e não no "quem" (quem escreveu).
- Não inserir assinaturas, saudações ou "easter eggs" no código-fonte ou em páginas públicas (Frontend e Mobile).

## 4. Prioridade de Decisão
- O proprietário (**Everton**) é a autoridade máxima. Planos de implementação devem ser validados e aprovados antes de execuções em larga escala que alterem a estrutura fundamental do diretório ou do design.

## 5. Estratégia de Branches (Git Flow)

| Branch | Finalidade | Regra |
|---|---|---|
| `main` | Produção estável (imaculada) | Só recebe merge DEPOIS que todos os testes passem. Zero exceções. |
| `release` | Integração com banco real | Aqui testamos com dados reais da aplicação. Toda integração com Neon/PostgreSQL deve estar imaculada. |
| `dev` | Desenvolvimento ativo | Base para criar branches de implementação e correção. |

- **Nomenclatura de branches:** `dev/nome_da_implementacao` (ex: `dev/fix_sync_timeout`, `dev/feature_export_csv`).
- **Fluxo:** `dev/feature_x` → PR para `dev` → PR para `release` (teste com dados reais) → PR para `main` (produção).
- **Regra de Ouro (Blindagem da Main):** 
    - Código sem teste não tem autorização de entrar em `main`.
    - **Protocolo de Auditoria Temporal:** Para qualquer `git push origin main`, o agente DEVE perguntar ao usuário: *"Que horas são?"* por **3 vezes consecutivas**. O agente deve validar se o horário fornecido pelo usuário coincide com o horário local do sistema. Se o desafio falhar, o push deve ser cancelado imediatamente. Isto evita execuções acidentais.


## 6. Testes — Independência e Cobertura

- **Cada suite de teste DEVE funcionar de forma independente** das outras suites. Nenhum teste pode depender de estado gerado por outro teste.
- **Sem teste = sem deploy.** Qualquer funcionalidade sem cobertura de teste não tem autorização de funcionar em produção.
- **TDD (Test-Driven Development)** é obrigatório para lógica de negócio:
  1. RED: Escrever o teste que falha.
  2. GREEN: Escrever o mínimo de código para passar.
  3. REFACTOR: Melhorar sem quebrar.

## 7. Padrões de Engenharia

Os seguintes padrões são obrigatórios e devem ser seguidos à risca:

- **Banco de Dados (Sem ORM):** ORM de cu é rola! Quem falar de instalar Prisma no projeto tá demitido sem justa causa. Aqui é SQL puro no terminal do banco de dados na veia.
- **SOLID:** Cada classe/módulo tem uma responsabilidade. Interfaces sobre implementações.
- **Clean Code:** Código autoexplicativo. Sem comentários óbvios. Nomes descritivos.
- **Design Patterns:** Aplicar quando resolver problema real (Repository, Service, Factory, Observer). Não forçar padrão onde não há necessidade.
- **Extreme Programming (XP):** Feedback rápido, simplicidade, iterações curtas.

## 8. Modularização — Cada Fluxo no Seu Quadrado

Os fluxos da aplicação são **independentes entre si**. Cada módulo deve poder ser testado, deployado e auditado isoladamente:

| Módulo | Escopo | Dependência Permitida |
|---|---|---|
| **Auth/Login** | Autenticação, JWT, RBAC | Nenhuma |
| **Leitura de Água** | Input, cálculo, persistência local | Auth (permissão) |
| **Sync** | Push/Pull, upload de foto | Auth (token) |
| **Relatórios** | Summary, timeseries, export PDF/CSV | Auth (token) |
| **Gestão de Usuários** | CRUD, LGPD, vincular medidores | Auth (admin) |
| **Tarifas** | CRUD de regras, ativação | Auth (admin) |
| **Alertas** | Anomalias, silenciamento | Auth (admin) |

- **PROIBIDO** acoplar a lógica de um módulo dentro de outro. Se o módulo de Relatórios precisa de dados de Leitura, ele acessa via serviço definido, não importando diretamente os internos.

### Documentação Modular (Independência de Contexto)
- **Cada módulo DEVE ter documentação autocontida** suficiente para que um novo desenvolvedor (humano ou IA) consiga dar continuidade ao desenvolvimento daquele fluxo **sem precisar ler o projeto inteiro**.
- Cada módulo deve manter na pasta `doc/modules/` um arquivo `{modulo}.md` contendo:
  - **Escopo:** O que o módulo faz e o que NÃO faz.
  - **Endpoints:** Rotas que pertencem ao módulo (referência ao `API_REFERENCE.md`).
  - **Schemas:** Validações de entrada e saída (Zod schemas aplicados).
  - **Dependências:** Quais outros módulos ele consome e como (interfaces, não implementações).
  - **Testes:** Onde estão os testes e como rodar isoladamente.
  - **Decisões:** Por que foi feito desta forma (link para `lessons_learned.md` se relevante).
- **Regra:** Se alguém precisa ler mais de 2 arquivos fora do módulo para entender como ele funciona, a documentação está incompleta.

## 9. Segurança — Independência e Auditabilidade

- **Cada camada de segurança deve funcionar de forma independente** e ser auditável pela dashboard.
- Todo acesso a recurso protegido DEVE gerar log registrado na tabela de auditoria.
- **Middlewares de segurança são auditáveis:**
  - `ensureAuthenticated` → Valida JWT e registra acesso
  - `ensureAdmin` → Valida role e registra tentativa
- Se uma camada de segurança falha, as demais continuam funcionando.
- Logs de segurança devem ser visíveis em `GET /api/logs` na dashboard.

## 10. Documentação — Padrão Obrigatório

A documentação é parte integral do desenvolvimento. Código sem documentação atualizada é código incompleto.

### 10.1 CHANGELOG por História
- **Cada história concluída** dentro de um épico DEVE gerar uma entrada no `CHANGELOG.md`.
- Formato obrigatório:
  ```
  ### [Épico X.Y] — Título da História (DD/MM/AAAA)
  - O que foi feito (resumo técnico)
  - Arquivos criados/modificados
  - Testes adicionados (quantidade e tipo)
  - Impacto em funcionalidades existentes
  ```
- O CHANGELOG é **cumulativo**: nunca apagar entradas anteriores.

### 10.2 Histórico de Desenvolvimento
- Manter `doc/requirements/backlog.md` atualizado com status real de cada épico.
- Toda decisão arquitetural significativa deve ser registrada em `doc/lessons_learned.md`.
- Cada épico finalizado deve ter seu documento de planejamento marcado com status `✅ CONCLUÍDO`.

### 10.3 Lições Aprendidas
- Ao final de cada épico, documentar em `doc/lessons_learned.md`:
  - **O que deu errado:** bugs, decisões ruins, retrabalho.
  - **O que deu certo:** padrões que funcionaram, decisões acertadas.
  - **O que mudar:** melhorias para o próximo épico.
- Lições aprendidas são fonte de verdade para evitar regressões.

### 10.4 Relatório de Segurança
- Manter `doc/security/` com os seguintes documentos atualizados:
  - **`security_layers.md`**: Documentação de cada camada de segurança implementada (Auth, RBAC, Middleware, Validação, Rate Limiting).
  - **`pentest_plan.md`**: Plano de testes de penetração com cenários a serem validados antes de cada release para `main`, incluindo:
    - Injeção SQL/NoSQL
    - Broken Authentication (JWT manipulation, token replay)
    - Broken Access Control (RBAC bypass, horizontal privilege escalation)
    - Mass Assignment / Overposting
    - File Upload vulnerabilities
    - Rate Limiting / DoS
    - CORS misconfiguration
  - **`vulnerability_log.md`**: Registro histórico de vulnerabilidades encontradas e como foram corrigidas.

### 10.5 Referência Técnica
- `doc/API_REFERENCE.md` deve estar sempre sincronizado com o código real das rotas.
- `doc/DATA_FLOW.md` deve refletir o fluxo real de dados (entrada, trânsito, saída).
- Qualquer alteração em schema Zod, rotas ou controllers exige atualização imediata nesses documentos.

### 10.6 Regra de Ouro da Documentação
> **Se o documento não reflete o estado real do código, ele é um risco — não um ativo.**
> Toda PR para `release` ou `main` deve incluir atualização de documentação correspondente.

### 10.7 Organização do Projeto e Nomenclaturas

Estes são **princípios universais** de organização. Valem para este projeto e para qualquer outro.

#### Princípio 1 — Separação por Camada
Todo projeto deve ter separação clara entre suas camadas na raiz:

| Camada | Responsabilidade |
|---|---|
| `backend/` ou `server/` | API, lógica de negócio, acesso a dados |
| `mobile/` ou `app/` | Aplicação mobile (Flutter, RN, etc.) |
| `web/` ou `dashboard/` | Frontend web |
| `doc/` | Documentação centralizada (nunca espalhada) |
| `RULES.md` | Lei do projeto — regras de desenvolvimento |
| `CHANGELOG.md` | Histórico cumulativo de entregas |
| `README.md` | Porta de entrada para qualquer dev novo |

#### Princípio 2 — Backend: Responsabilidade Única por Pasta
```
src/
├── controllers/     # Orquestração HTTP (recebe request, retorna response)
├── services/        # Lógica de negócio pura (testável sem HTTP)
├── routes/          # Definição de rotas e middlewares aplicados
├── middlewares/     # Auth, validação, rate limiting
├── schemas/         # Validação de entrada (Zod, Joi, etc.)
├── models/ ou prisma/  # Definição de dados e migrações
├── testes/
│   ├── helpers/     # Fixtures, tokens fake, factories
│   ├── integration/ # {modulo}.spec.ts — Teste com HTTP real
│   └── unit/        # {modulo}.test.ts — Teste isolado
└── app.ts           # Entry point (sem server.listen para testabilidade)
```

#### Princípio 3 — Mobile: Telas Encontráveis em 2 Cliques
```
lib/
├── features/                # Uma pasta por domínio de negócio
│   └── {modulo}/
│       ├── views/           # 🖥️ TELAS — Onde o usuário interage
│       ├── controllers/     # Lógica de tela, estado
│       ├── models/          # Entidades do domínio
│       ├── repositories/    # Acesso a dados local (SQLite, cache)
│       └── services/        # Comunicação externa (API, sync)
├── core/                    # Theme, constants, widgets compartilhados
├── navigation/              # Rotas e navegação centralizada
└── main.dart                # Entry point
```
> **Regra dos 2 cliques:** Um dev novo deve encontrar qualquer tela em `features/{modulo}/views/`. Se ele precisar navegar mais de 2 pastas para achar onde uma tela vive, a organização está errada.

#### Princípio 4 — Dashboard/Web: Pages São o Ponto de Entrada
```
src/
├── pages/           # Uma por rota do app — ponto de entrada visual
├── components/      # Reutilizáveis, sem lógica de negócio
├── services/        # API calls, auth helpers
├── hooks/ ou stores/ # Estado global/compartilhado
└── App.tsx          # Routing + Providers
```

#### Princípio 5 — Documentação Segregada
```
doc/
├── requirements/    # RF, RNF, backlog
├── planning/        # Planejamento de épicos e sprints
├── qa/              # Mapas de testes, planos de QA
├── security/        # Camadas, pentest, vulnerabilidades
└── modules/         # Doc autocontida por módulo (ver §8)
```

#### Princípio 6 — Nomenclaturas (camelCase é padrão)

| Tipo | Padrão | Exemplo |
|---|---|---|
| Arquivo código | `camelCase` com sufixo de responsabilidade | `auth.controller.ts`, `syncService.dart` |
| Pasta | `camelCase` | `features/`, `controllers/`, `views/` |
| Classe | `PascalCase` | `SyncController`, `ReadingRepository` |
| Variável/Função | `camelCase` | `pushReadings`, `adminToken` |
| Constante | `UPPER_SNAKE_CASE` | `JWT_SECRET`, `MAX_UPLOAD_SIZE` |
| Tabela DB | `snake_case` plural | `readings`, `tariff_rules` |
| Branch | `dev/descricao` | `dev/fix_sync_timeout` |
| Teste Backend | `{modulo}.spec.ts` | `auth.spec.ts` |
| Teste Mobile | `{feature}Test.dart` | `readingValidationTest.dart` |

> **Princípio geral:** Se o nome do arquivo não diz o que ele faz e onde ele mora, renomeie.
> 
> **Aditivo Mobile (Flutter):** Excepcionalmente no projeto Mobile, os nomes de arquivos e pastas devem seguir o padrão `snake_case` (ex: `sync_service.dart`). Este aditivo visa manter a compatibilidade com as ferramentas de linting e o ecossistema padrão do Flutter, evitando conflitos com o framework. No Dashboard e Backend, o padrão `camelCase` permanece obrigatório.

## 11. O Ciclo de Aprendizado por Erro (Pivagem Técnica)

- **Erros são balizadores:** Cada falha técnica que exigir mais de 2 tentativas de correção DEVE ser tratada como um sinal de que há um conhecimento oculto ou uma assunção errada.
- **Registro de Post-Mortem:** O agente deve registrar em `doc/lessons_learned.md` o seguinte para cada "cabeçada" dada:
    - **Assunção Original:** O que eu achava que ia funcionar.
    - **Causa Real do Erro:** O detalhe técnico que estava impedindo o acerto.
    - **A Solução "Pulo do Gato":** Como resolver de forma definitiva.
- **Uso Transversal:** Essas lições devem ser consultadas pelo agente antes de iniciar novas implementações similares para evitar a repetição de erros caros.

---
*Atualizado em 07 de Abril de 2026 por Everton Lyons Romansini (com contribuição da IA).*

