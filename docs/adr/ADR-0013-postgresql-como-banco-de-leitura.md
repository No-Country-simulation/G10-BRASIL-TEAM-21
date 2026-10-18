# ADR-0013 — PostgreSQL como banco de leitura; Object Storage como arquivo e evidência

- **Status:** Aceito
- **Data:** 2026-10-17
- **Decisores:** Equipe AdaptAI (Grupo 10)
- **Substitui:** [ADR-0005](./ADR-0005-oci-object-storage-como-persistencia.md). Também **sobrescreve** o item de armazenamento de usuários do [ADR-0006](./ADR-0006-autenticacao-jwt-simples.md) (usuários e índice por e-mail como objetos JSON). O restante do ADR-0006 (JWT, bcrypt, logout no cliente) segue válido.

## Contexto

O ADR-0005 escolheu o Object Storage como persistência única, sem banco, e registrou as consequências: sem transações (o XP vira *ler, alterar e gravar*), listagens dependentes de prefixos e de objetos de índice, e nenhum índice definido para o histórico de adaptações.

Duas necessidades novas pesam contra essa escolha:

1. O front-end precisa **listar, filtrar e relacionar** resultados com o usuário (histórico, perfil, conceitos), o que é consulta, não leitura de arquivo.
2. O XP tem teto diário e pontuação única por pergunta. Garantir isso com *ler, alterar e gravar* depende da premissa "sem concorrência por usuário", que um banco com transações dispensa.

O edital exige o OCI Object Storage para os documentos originais e os JSONs gerados, mas **não proíbe** um banco adicional.

## Decisão

1. **PostgreSQL 16** em container, no Docker Compose da raiz do monorepo ([ADR-0015](./ADR-0015-docker-compose-e-backend-unico.md)), com a extensão `pgvector` ([ADR-0014](./ADR-0014-pgvector-como-vector-store.md)). Esquema e migrações com **SQLAlchemy 2.x e Alembic**.
2. O **banco é a fonte de leitura do produto**: usuários, perfil e XP, documentos (metadados), chunks, adaptações (colunas de metadados mais o JSON completo em `JSONB`), eventos de XP, conceitos e testes de nível. O front-end lê só do banco, via API.
3. O **bucket é arquivo e evidência**. Um único bucket Always Free (`AdaptAI-conteudos-educativos`), com os prefixos `documentos/`, `adaptacoes/` e `backups/`. Guarda os documentos originais, o JSON final de cada adaptação e os backups do banco.
4. **Ordem de gravação** em `POST /adaptacoes`:
   1. transação no banco com o resultado, o XP e `status_upload = pendente`;
   2. envio do original e do JSON ao bucket;
   3. atualização de `status_upload` para `concluido` ou `falha`.

   A resposta ao cliente traz o `status_upload` final. Se o bucket falhar, o resultado **não se perde**, e um script idempotente reenvia os pendentes.
5. **Recuperação:** documentos e adaptações são reconstruíveis a partir do bucket (script de reindexação e reenvio). Usuários, perfis e XP existem só no banco, portanto há `pg_dump` periódico para `backups/`.
6. **Acesso por interfaces (ports):** `StoragePort` (`OCIObjectStorage` e `LocalFileStorage`) e repositórios (SQL e versões em memória para testes).
7. **Mantido do ADR-0005:** autenticação na OCI com o SDK para Python por chave de API em variáveis de ambiente; cada novo recurso na OCI só é criado após confirmar que é **Always Free**.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Autonomous Database Always Free | Segundo a documentação da Oracle: 1 CPU e 20 GB sem escala, parada automática após 7 dias sem atividade e possível remoção após cerca de 90 dias parado. Exige carteira (*wallet*) e conexão específica, com dialeto diferente do ambiente local. Conferir os limites vigentes antes de reavaliar |
| SQLite | Sem `pgvector`; arquivo local; diferença entre desenvolvimento e demonstração |
| MySQL | Sem equivalente ao `pgvector` na stack escolhida; exigiria Chroma como componente extra |
| Somente o bucket (ADR-0005) | Histórico por listagem de prefixo e XP sem transação |
| PostgreSQL gerenciado da OCI | Não avaliado. Só considerar se for confirmado Always Free |

## Consequências

**Positivas**
- Listagem, filtros e relações entre usuário, documento e resultado por consulta.
- XP consistente: a linha do perfil é travada na transação (`SELECT ... FOR UPDATE`), e o acerto único por pergunta é garantido por índice único.
- A mesma imagem do banco roda em desenvolvimento, demonstração e VM.
- A leitura do front não depende da disponibilidade da OCI.

**Negativas e riscos**
- **Duas persistências podem divergir.** Mitigação: `status_upload`, reenvio idempotente e reindexação a partir do bucket.
- **Banco com estado na VM.** Mitigação: volume nomeado no Compose e `pg_dump` periódico para `backups/`.
- Mais componentes (conexão, migrações, backup) no mesmo prazo, e mais memória na VM.
- O ADR-0001 rejeitou o Django citando "uma API sem banco relacional". Com o banco, esse argumento enfraquece, mas o FastAPI segue adequado (OpenAPI e Pydantic). Sem ação.

## Referências
[03 - Modelo de Domínio](../03%20-%20Modelo%20de%20Dom%C3%ADnio.md#7-esquema-do-banco-postgresql) · [04 - Arquitetura](../04%20-%20Arquitetura.md) · US-006, US-007, US-008, US-035 a US-038 · [Documentação do Autonomous Database Always Free](https://docs.oracle.com/iaas/autonomous-database-shared/doc/autonomous-always-free.html)
