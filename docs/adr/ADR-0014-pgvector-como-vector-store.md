# ADR-0014 — `pgvector` como vector store (índice reconstruível a partir do bucket)

- **Status:** Aceito
- **Data:** 2026-10-17
- **Decisores:** Equipe AdaptAI (Grupo 10)
- **Substitui:** [ADR-0003](./ADR-0003-rag-com-chroma-e-indice-reconstruivel.md). Os parâmetros de chunking e recuperação do ADR-0003 são **mantidos**.

## Contexto

O ADR-0003 escolheu o Chroma local como vector store, com uma coleção por documento, tratado como cache reconstruível. Com o PostgreSQL já adotado ([ADR-0013](./ADR-0013-postgresql-como-banco-de-leitura.md)), manter o Chroma significa um segundo armazenamento de estado, com seu próprio diretório e ciclo de vida, só para vetores.

O edital pede "busca vetorial em Vector Store (ex.: Chroma, FAISS ou similar)". Uma extensão vetorial do Postgres é uma solução equivalente.

## Decisão

1. **`pgvector`** no mesmo PostgreSQL, em uma tabela `chunks` com a coluna `embedding vector(N)`.
2. **N é a dimensão do modelo de embeddings** escolhido no [ADR-0011](./ADR-0011-provedor-de-llm-e-embeddings.md). Trocar o modelo exige recriar a coluna e **reindexar** todos os documentos.
3. **Isolamento:** toda consulta vetorial filtra por `documento_id`, resolvido a partir do `usuario_id` do token. Não há coleção global sem filtro.
4. **Chunking** com `RecursiveCharacterTextSplitter`, ponto de partida de **900 caracteres e 150 de sobreposição**, `chunk_id` determinístico (`chunk-001`, ...), como no ADR-0003.
5. **Recuperação** com `top_k` inicial de **6** e métrica de distância por cosseno. Documentos curtos (até cerca de 12 chunks) entram inteiros no contexto; documentos longos usam busca por tópico do plano.
6. **Índice reconstruível:** a fonte da verdade dos documentos continua sendo o original em `documentos/` no bucket. Se a tabela `chunks` for perdida, um script a recria (US-013).
7. **Índice vetorial:** a busca exata basta para o volume esperado. Criar um índice HNSW ou IVFFlat só se a medição mostrar necessidade. Decidir no spike.
8. **Biblioteca de acesso** (integração do LangChain com Postgres ou SQL direto): decidir no spike da semana 1, conferindo a versão vigente.

Os valores numéricos são ponto de partida, **calibrados na semana 2** com o documento de exemplo.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Chroma embutido ou em container | Segundo componente de estado ao lado do Postgres, sem ganho para o escopo |
| FAISS | Sem metadados e persistência nativos |
| Índice vetorial do Autonomous Database | Descartado junto com o banco no ADR-0013 |
| Banco vetorial gerenciado | Custo e risco de sair da camada Always Free |

## Consequências

**Positivas**
- Um componente a menos: vetores, documentos e usuários no mesmo banco, com backup e transação únicos.
- Filtro por documento e por usuário em SQL.
- Chunks determinísticos continuam permitindo citar `fontes_chunks` de forma estável.

**Negativas e riscos**
- O banco precisa de uma imagem do Postgres com a extensão `pgvector`. Confirmar a imagem e a compatibilidade com a arquitetura da VM (ver [ADR-0015](./ADR-0015-docker-compose-e-backend-unico.md)).
- Dimensão fixa por modelo: trocar o embedding custa reindexação.
- Menos ajustes finos de recuperação do que em um motor dedicado. Aceitável para o volume do MVP.
- Documentos curtos dispensam a busca vetorial na geração. A indexação acontece, mas a recuperação não é exercitada. Ver o risco em [04 - Arquitetura](../04%20-%20Arquitetura.md#13-riscos-técnicos-e-mitigações).

## Referências
[04 - Arquitetura](../04%20-%20Arquitetura.md#5-pipeline-rag) · US-010 a US-013
