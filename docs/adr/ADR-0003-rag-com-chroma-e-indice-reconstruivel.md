# ADR-0003 — RAG com Chroma e índice reconstruível

- **Status:** Substituído por [ADR-0014](./ADR-0014-pgvector-como-vector-store.md)
- **Data:** 2026-10-13
- **Decisores:** Equipe AdaptAI (Grupo 10)

## Contexto

O edital exige RAG com chunking, embeddings e busca vetorial em *vector store*, e persistência dos arquivos no OCI Object Storage. Não há banco vetorial gerenciado na camada Always Free que queiramos adotar. Reinícios da aplicação não podem fazer o usuário perder documentos.

## Decisão

1. **Chroma** local persistente como *vector store*, com **uma coleção por documento** (`doc_{documento_id}`).
2. O diretório do Chroma é tratado como **cache reconstruível**: a fonte da verdade são os originais no bucket (`documentos/`). Se uma coleção não existir, ela é recriada a partir do original.
3. **Chunking** com `RecursiveCharacterTextSplitter`, ponto de partida de **900 caracteres e 150 de sobreposição**, `chunk_id` determinístico.
4. **Recuperação** com `top_k` inicial de **6**. Documentos curtos (até cerca de 12 chunks) entram inteiros no contexto; documentos longos usam busca por tópico do plano.

Os valores numéricos são ponto de partida, **calibrados na semana 2** com o documento de exemplo.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| FAISS | Sem metadados e persistência nativos; exigiria mais código para o mesmo resultado |
| Índice persistido no bucket como fonte da verdade | Aumenta complexidade de sincronização sem benefício no MVP |
| Banco vetorial gerenciado | Custo e risco de sair da camada Always Free |
| Uma coleção global para todos os usuários | Risco de misturar documentos de usuários diferentes |

## Consequências

**Positivas**
- Isolamento natural por documento e por usuário.
- Reinício, troca de máquina e deploy não perdem dados.
- Chunks determinísticos permitem citar `fontes_chunks` de forma estável.

**Negativas e riscos**
- Reconstrução custa tempo e embeddings na primeira consulta após perda do índice. Mitigação: script de reindexação e reconstrução sob demanda.
- Qualidade da recuperação depende do chunking. Mitigação: calibrar na semana 2 e validar com perguntas de teste.

## Referências
[04 - Arquitetura](../04%20-%20Arquitetura.md#5-pipeline-rag) · US-010 a US-013
