# ADRs — Registros de Decisões de Arquitetura

Cada ADR registra **uma decisão**, o contexto em que foi tomada, as alternativas descartadas e as consequências. ADRs aceitos **não são editados**: se a decisão mudar, cria-se um novo ADR que o **substitui** (e o anterior passa a `Substituído por ADR-XXXX`).

**Status possíveis:** `Proposto` · `Em aberto` · `Aceito` · `Substituído`

| ADR | Decisão | Status |
|---|---|---|
| [ADR-0001](./ADR-0001-python-e-fastapi-no-backend.md) | Python e FastAPI no back-end | Aceito |
| [ADR-0002](./ADR-0002-front-end-desacoplado-sem-streamlit.md) | Front-end desacoplado, sem Streamlit | Aceito |
| [ADR-0003](./ADR-0003-rag-com-chroma-e-indice-reconstruivel.md) | RAG com Chroma e índice reconstruível | Substituído por [ADR-0014](./ADR-0014-pgvector-como-vector-store.md) |
| [ADR-0004](./ADR-0004-langgraph-para-orquestracao.md) | LangGraph para orquestração | Aceito |
| [ADR-0005](./ADR-0005-oci-object-storage-como-persistencia.md) | OCI Object Storage como persistência única | Substituído por [ADR-0013](./ADR-0013-postgresql-como-banco-de-leitura.md) |
| [ADR-0006](./ADR-0006-autenticacao-jwt-simples.md) | Autenticação simples com JWT | Aceito (o armazenamento de usuários em objetos JSON foi substituído pelo [ADR-0013](./ADR-0013-postgresql-como-banco-de-leitura.md); o restante segue válido) |
| [ADR-0007](./ADR-0007-analogias-separadas-do-conteudo-ancorado.md) | Analogias separadas do conteúdo ancorado; busca na web adiada | Aceito |
| [ADR-0008](./ADR-0008-niveis-por-usuario-xp-e-teste-de-nivel.md) | Níveis por usuário, XP validado e Teste de Nível | Aceito |
| [ADR-0009](./ADR-0009-contrato-json-estendido-compativel-com-edital.md) | Contrato JSON estendido e compatível com o edital | Aceito |
| [ADR-0010](./ADR-0010-verificacao-de-fidelidade-por-juiz-llm.md) | Verificação de fidelidade por juiz LLM | Aceito (calibrar na semana 3) |
| [ADR-0011](./ADR-0011-provedor-de-llm-e-embeddings.md) | Provedor de LLM e embeddings | **Proposto** (confirmar na semana 1; define a dimensão do `pgvector`) |
| [ADR-0012](./ADR-0012-framework-do-front-end.md) | Framework do front-end | **Em aberto** (decidir na semana 1) |
| [ADR-0013](./ADR-0013-postgresql-como-banco-de-leitura.md) | PostgreSQL como banco de leitura; Object Storage como arquivo e evidência | Aceito |
| [ADR-0014](./ADR-0014-pgvector-como-vector-store.md) | `pgvector` como vector store (índice reconstruível a partir do bucket) | Aceito |
| [ADR-0015](./ADR-0015-docker-compose-e-backend-unico.md) | Docker Compose, backend único e VM como bônus | Aceito |
| [ADR-0016](./ADR-0016-sqlalchemy-psycopg-pgvector.md) | SQLAlchemy 2.x, psycopg 3 e pgvector para acesso a dados | Aceito |

## Modelo para novos ADRs

```markdown
# ADR-NNNN — Título da decisão

- **Status:** Proposto | Em aberto | Aceito | Substituído por ADR-XXXX
- **Data:** AAAA-MM-DD
- **Decisores:** quem decidiu

## Contexto
## Decisão
## Alternativas consideradas
## Consequências
## Referências
```
