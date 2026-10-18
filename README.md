# AdaptAI

Adaptação de conteúdo educacional por perfil, com RAG e verificação de fidelidade. Hackathon ONE G10.
Contexto de produto, requisitos, arquitetura, contrato de API e backlog estão em [`docs/`](docs/README.md).

## Rodando localmente

Requisito: Docker com Compose.

```bash
cp .env.example .env     # preencha JWT_SECRET e POSTGRES_PASSWORD (só letras e números na senha)
docker compose up --build
curl http://localhost:8000/api/v1/health
```

O serviço `frontend` só builda depois que o projeto Vite for criado e commitado (ver `frontend/README.md`).

Swagger em `http://localhost:8000/docs`. Nunca versione o `.env`.

## Estrutura

```text
backend/    API FastAPI (camadas: api, services, agents, rag, domain, ports, infra)
frontend/   interface React + Vite (ADR-0012) e mocks do contrato
docs/       visão, requisitos, arquitetura, contrato, ADRs, PRDs
.github/    template de PR e CODEOWNERS (o CI será criado pelo DevOps; sugestão em docs/ci-sugestao/)
docker-compose.yml   Postgres 16 + pgvector, backend e frontend
```

## Fluxo de trabalho

Branches, commits e PRs seguem a seção 5 de [`docs/07 - Convenções.md`](docs/07%20-%20Conven%C3%A7%C3%B5es.md).
Resumo: `feat/back-…`, `feat/front-…`, `feat/agent-…` saem de `dev` e voltam por PR (squash); `dev` → `homolog` → `main`
por PR com merge commit. Commits e títulos de PR em Conventional Commits (PT-BR).

## Decisões em aberto

LLM e embeddings (ADR-0011) e conta e região da OCI.
