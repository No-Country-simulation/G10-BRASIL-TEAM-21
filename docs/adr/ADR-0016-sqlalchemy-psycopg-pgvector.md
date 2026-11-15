# ADR-0016 — SQLAlchemy 2.x, psycopg 3 e pgvector para acesso a dados

- **Status:** Aceito
- **Data:** 2026-10-25
- **Decisores:** Equipe AdaptAI (Grupo 10)

## Contexto

A T2 (US-008) requer uma solução de ORM, um driver PostgreSQL e suporte a vetores para o acesso aos dados da aplicação. É necessário registrar as tecnologias utilizadas e definir como elas se integram às migrações do banco de dados.

## Decisão

1. Utilizar **SQLAlchemy 2.x**, com mapeamento declarativo tipado por `Mapped`, e **Alembic** para gerenciar as migrações.
2. Utilizar **psycopg 3** como driver PostgreSQL, com URLs no formato `postgresql+psycopg://...`.
3. Utilizar a biblioteca Python **pgvector** para representar vetores no PostgreSQL. A dependência já está declarada em `backend/pyproject.toml`.
4. Criar a extensão PostgreSQL `vector` na migração `0001`. A coluna `chunks.embedding` será adicionada em uma migração posterior, quando a dimensão for definida conforme o ADR-0011.
5. Utilizar sessões síncronas do banco de dados nas rotas que acessam diretamente essa camada; essas rotas devem usar `def`, em vez de `async def`, salvo se houver uma estratégia explícita para executar as operações bloqueantes fora do event loop.

## Alternativas consideradas

| Alternativa | Justificativa para não adoção |
|---|---|
| SQLAlchemy com driver assíncrono | A stack atual utiliza sessões síncronas; introduzir acesso assíncrono exigiria adaptar a configuração e o gerenciamento das sessões. |
| Adicionar `pgvector` somente quando a coluna for criada | A dependência já está declarada no projeto; sua utilização efetiva na coluna será implementada junto à migração correspondente. |

## Consequências

**Positivas**

- O SQLAlchemy centraliza o mapeamento entre modelos Python e tabelas do PostgreSQL.
- O Alembic permite versionar as alterações do esquema do banco de dados.
- O pgvector viabiliza o armazenamento e a consulta de embeddings no PostgreSQL.

**Negativas e riscos**

- A dimensão de `chunks.embedding` depende da definição registrada no ADR-0011.
- Alterações nos modelos e nas migrações devem ser revisadas em conjunto no mesmo PR.
- A verificação `alembic check` no CI ajuda a identificar diferenças entre os modelos e o esquema migrado.

## Referências

- ADR-0011 — Provedor de LLM e embeddings.
- ADR-0013 — PostgreSQL como banco de leitura.
- ADR-0014 — pgvector como vector store.
- ADR-0015 — Docker Compose, backend único e VM como bônus.
- `backend/pyproject.toml` — dependências do backend.