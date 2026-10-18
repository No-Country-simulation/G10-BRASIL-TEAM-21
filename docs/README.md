# Documentação do adaptai

**adaptai** — Sistema Inteligente de Adaptação e Geração de Conteúdo Educacional · Hackathon ONE G10 (Oracle Next Education & Alura)

> Versão da documentação: v2 · 2026-10-17 · Primeira entrega: 24/11/2026

## Índice

| # | Documento | Para quê |
|---|---|---|
| 01 | [Visão de produto](./01%20-%20Vis%C3%A3o%20de%20produto.md) | Problema, proposta de valor, escopo, metas e rastreabilidade com o edital |
| 02 | [Requisitos](./02%20-%20Requisitos.md) | Requisitos funcionais, não funcionais e regras de negócio |
| 03 | [Modelo de Domínio](./03%20-%20Modelo%20de%20Dom%C3%ADnio.md) | Entidades, enumerações, estados, esquema do banco e layout do bucket |
| 04 | [Arquitetura](./04%20-%20Arquitetura.md) | Componentes, fluxo RAG e agentes, segurança, execução e riscos técnicos |
| 05 | [Contrato de API](./05%20-%20Contrato%20de%20API.md) | Endpoints, JSON estendido e códigos de erro |
| 06 | [Backlogs](./06%20-%20Backlogs.md) | Épicos, histórias com critérios de aceite, cronograma e gates |
| 07 | [Convenções](./07%20-%20Conven%C3%A7%C3%B5es.md) | Código, banco, Git, testes, segredos e documentação |
| 08 | [Mapas de Competências](./08%20-%20Mapas%20de%20Compet%C3%AAncias.md) | Formações ONE, competências e plano de estudo |
| — | [ADRs](./adr/README-ADR.md) | Decisões de arquitetura registradas |
| — | [PRDs](./prd/README-PRD.md) | Requisitos de produto por funcionalidade |

## O que mudou na v2 (17/10/2026)

- **Persistência:** PostgreSQL como banco de leitura (usuários, resultados e histórico) e OCI Object Storage como arquivo e evidência ([ADR-0013](./adr/ADR-0013-postgresql-como-banco-de-leitura.md), substitui o ADR-0005).
- **Vector store:** `pgvector` no mesmo PostgreSQL ([ADR-0014](./adr/ADR-0014-pgvector-como-vector-store.md), substitui o ADR-0003).
- **Execução:** Docker Compose na raiz do monorepo, um único processo de backend e a VM da OCI como bônus ([ADR-0015](./adr/ADR-0015-docker-compose-e-backend-unico.md)).
- **Regras novas:** RN-17 (persistência dupla), RN-18 (nível do documento estimado na ingestão) e RN-19 (linguagem figurada permitida; o juiz avalia só afirmações factuais).
- **Contrato:** `analogias` e `microlearning` no nível superior; `status_upload` também em documentos; erro `BANCO_INDISPONIVEL`.
- **Cronograma:** refeito a partir de 18/10 (5 semanas e 2 dias). Login (MVP) passou para a semana 2; Gate 1 em 7/11; congelamento em 20/11.

## Decisões em aberto

| Item | Onde | Prazo |
|---|---|---|
| Provedor de LLM e embeddings (define a dimensão da coluna vetorial) | [ADR-0011](./adr/ADR-0011-provedor-de-llm-e-embeddings.md) | Fim da semana 1 |
| Composição da equipe, responsáveis e horas por semana | [08 - Mapas de Competências](./08%20-%20Mapas%20de%20Compet%C3%AAncias.md) | Planning da semana 1 |
| Criação da conta OCI e da região principal | [06 - Backlogs](./06%20-%20Backlogs.md#5-riscos-que-afetam-o-backlog) (R1) | Semana 1 |
| Documento do terceiro cenário de demo e documento longo | [06 - Backlogs](./06%20-%20Backlogs.md#3-cen%C3%A1rios-de-demonstra%C3%A7%C3%A3o-us-090) | Antes da semana 3 |
| Datas e rubrica da fase final | Organizadores do hackathon | Semana 1 |
| Calibragem de limiares de XP e do método de fidelidade | PRD-003 e ADR-0010 | Semanas 3 e 4 |

## Como manter esta documentação

Mudou uma regra de negócio, o contrato ou a arquitetura? **Atualize o documento no mesmo PR.** Decisões difíceis de reverter viram ADR; funcionalidades novas ganham PRD. Os títulos dos documentos são âncoras de link: ao renomear um, corrija os links que apontam para ele. Detalhes em [07 - Convenções](./07%20-%20Conven%C3%A7%C3%B5es.md#8-documenta%C3%A7%C3%A3o).
