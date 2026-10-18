# 08 - Mapas de Competências

> **Versão:** v2 · **Data:** 2026-10-17
> Conecta o projeto às **formações do Programa ONE (Grupo 10)**, mostra onde cada competência é aplicada e organiza o estudo da equipe entre 18/10 e 24/11/2026.

---

## 1. Formações do Grupo 10 e papel no projeto

| Formação | Tipo | Núcleo no AdaptAI |
|---|---|---|
| Inteligência de Dados e RAG Avançado | Indispensável | Pipeline RAG: chunking, embeddings e busca vetorial (`pgvector`) para ancorar o conteúdo |
| Oracle Cloud Infrastructure (OCI) | Indispensável | Object Storage na camada Always Free; opcionalmente, Compute |
| Engenharia de Agentes e Automação | Reforço | Grafo de agentes (pesquisador, redator, revisor) e automação do fluxo |
| Desarrollo y Orquestación con IA Generativa | Reforço | Prompts estruturados, few-shot, role prompting e orquestração com LLMs |

## 2. Competências aplicadas no projeto

| Competência | Onde é aplicada | Épico ou documento | ADR |
|---|---|---|---|
| Extração e limpeza de texto de PDF e Markdown | Ingestão de documentos | E1 · US-010 | ADR-0014 |
| Estratégias de *chunking* | Segmentação do texto | E1 · US-011 | ADR-0014 |
| Embeddings e busca vetorial com `pgvector` | Indexação e recuperação no PostgreSQL | E1 · US-012 | ADR-0014, ADR-0011 |
| Avaliação de RAG e mitigação de alucinação | Score de fidelidade e rastreio de fontes | E3 · US-031, US-032 | ADR-0010 |
| Engenharia de prompts (few-shot, role prompting) | Redação por formato, perfil e nicho | E2 · US-022, US-023 | ADR-0011 |
| Saídas estruturadas | JSON validado por Pydantic | E2 · US-021, US-025 | ADR-0009 |
| Orquestração com grafos (LangGraph) | Recuperar, planejar, redigir, verificar | E2 e E3 | ADR-0004 |
| Padrões de agentes (crítico e revisor) | Verificação e reescrita única | E3 · US-031 | ADR-0004, ADR-0010 |
| OCI Object Storage via SDK | Arquivo e evidência: originais, JSONs e backups | E4 · US-006, US-035, US-036 | ADR-0013 |
| Cotas e custos Always Free | Governança de recursos da OCI | Todos | ADR-0013, ADR-0015 |
| Deploy em OCI Compute | Hospedagem da aplicação (opcional) | E10 · US-093 | ADR-0015 |
| Automação e integração entre serviços | Fluxo ponta a ponta da adaptação | E2, E4 | ADR-0001, ADR-0013 |

## 3. Competências complementares (além das formações)

| Competência | Onde é aplicada | Observação |
|---|---|---|
| API REST com FastAPI e OpenAPI | Back-end e contrato | ADR-0001 |
| PostgreSQL, SQLAlchemy e migrações com Alembic | Banco de leitura, usuários, resultados e XP | ADR-0013 · US-008 |
| Docker e Docker Compose | Stack reproduzível local e na VM | ADR-0015 · US-007 |
| Transações e consistência entre banco e bucket | Dupla persistência, reenvio e backup | ADR-0013 · US-036, US-038 |
| Autenticação com JWT e bcrypt | Login simples | ADR-0006 |
| Modelagem de domínio e regras de negócio | Trilha de Evolução | ADR-0008 |
| Front-end SPA consumindo OpenAPI | Interface | ADR-0002, ADR-0012 |
| Testes de regras puras, de contrato e de integração com o banco | Qualidade | [07 - Convenções](./07%20-%20Conven%C3%A7%C3%B5es.md) |
| Git colaborativo e revisão de código | Todo o projeto | [07 - Convenções](./07%20-%20Conven%C3%A7%C3%B5es.md) |
| Design pedagógico (níveis, analogias, microlearning) | Motor de analogias e trilha | PRD-003 a PRD-005 |

## 4. Papéis sugeridos e competências exigidas

**A composição da equipe ainda não foi definida**: número de pessoas, quem faz o front-end e as horas por semana de cada um são dados em aberto. Os papéis abaixo existem para a planning da semana 1; um papel pode ser acumulado por mais de uma pessoa, e **uma pessoa pode precisar cobrir todos eles** até alguém assumir uma tarefa com prazo.

| Papel | Foco | Competências principais | Responsável |
|---|---|---|---|
| Back-end e IA (RAG e agentes) | Ingestão, RAG, grafo, fidelidade | RAG, `pgvector`, LangGraph, prompts, Pydantic | a definir |
| Back-end de plataforma | API, autenticação, banco, OCI, evolução, Compose | FastAPI, SQLAlchemy, Alembic, OCI SDK, JWT, Docker, testes | a definir |
| Front-end | Telas e consumo do contrato | SPA, OpenAPI, UX de formatos | a definir |
| Produto, QA e documentação | Backlog, cenários de demo, README | Escrita técnica, validação, apresentação | a definir |

## 5. Plano de estudo por semana

| Semana | Tema de estudo | Quem mais precisa |
|---|---|---|
| 1 (18 a 24/10) | Docker Compose e PostgreSQL com `pgvector`; SQLAlchemy e Alembic; OCI Object Storage e SDK (spike); FastAPI e Pydantic; geração de tipos a partir do OpenAPI | Back-end de plataforma e front-end |
| 2 (25 a 31/10) | JWT e bcrypt; chunking e embeddings; leitura de PDF | Back-end de plataforma; back-end e IA |
| 3 (1 a 7/11) | LangGraph e saídas estruturadas; avaliação de fidelidade; transações e reenvio entre banco e bucket | Back-end e IA; back-end de plataforma |
| 4 (8 a 14/11) | Regras de gamificação e testes de regras puras; concorrência com `SELECT ... FOR UPDATE` | Back-end de plataforma; produto |
| 5 (15 a 21/11) | Prompts por nicho; microlearning; polimento de UI | Back-end e IA; front-end |
| Final (22 a 24/11) | Escrita do README; ensaio de apresentação; OCI Compute (opcional) | Todos |

## 6. Lacunas e como tratá-las

- **Competência concentrada em uma pessoa** (por exemplo, só uma pessoa entende o grafo ou o banco): programar em dupla nas semanas 2 e 3 e revisar PRs cruzados.
- **Tema novo para todos** (por exemplo, juiz de fidelidade ou `pgvector`): reservar um *spike* curto de meio dia, com resultado registrado no ADR correspondente.
- **Equipe sem composição definida:** ver o risco R2 em [06 - Backlogs](./06%20-%20Backlogs.md#5-riscos-que-afetam-o-backlog).
- **Atualize esta tabela** quando um ADR mudar uma tecnologia.
