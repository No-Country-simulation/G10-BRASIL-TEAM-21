# Backend (FastAPI)

Um único processo Python: API, regras de serviço, grafo de agentes e RAG são **camadas** do mesmo
código (ADR-0015). Estrutura e regras de dependência em `docs/04 - Arquitetura.md` (seção 7) e
`docs/07 - Convenções.md` (seção 2).

## Estado atual

Esqueleto: `GET /api/v1/health`, configuração por ambiente e dois testes. O restante entra pelo backlog
(`docs/06 - Backlogs.md`): banco e migrações (US-008), login (US-040 a US-045), ingestão e RAG
(US-010 a US-014), grafo (US-021 em diante).

## Comandos

Pelo Compose, a partir da raiz do repositório:

```bash
cp .env.example .env        # preencha JWT_SECRET e POSTGRES_PASSWORD
docker compose up --build
curl http://localhost:8000/api/v1/health
# Swagger: http://localhost:8000/docs
```

Direto na máquina, a partir desta pasta:

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check . && ruff format --check .
pytest
```

## Estrutura

```text
app/
├── main.py        criação do app, CORS
├── config.py      configuração lida do ambiente (sem segredo com valor padrão)
├── api/           routers
├── schemas/       modelos Pydantic (contrato)
├── domain/        regras puras, sem I/O
├── services/      casos de uso
├── agents/        grafo LangGraph
├── rag/           extração, chunking, embeddings, recuperação
├── ports/         interfaces
└── infra/         implementações (PostgreSQL, OCI, LLM)
tests/
scripts/           seed do usuário demo, reindexação, reenvio de pendências, backup
```

`migrations/` e `alembic.ini` serão criados na US-008.
