# Spike LLM — gemini / gemini-3.8-flash

Embeddings: `gemini-embedding-001`. Repetições: 1.

## Geração (3 cenários, mesmo documento)

| Cenário | Perfil / formato / nicho | Latência (s) | Tokens ent./saída | JSON | Schema | Chunks | Itens | Erro |
|---|---|---|---|---|---|---|---|---|
| A | Iniciante / Flashcards / Geral | 90.22 | None/None | NÃO | NÃO | NÃO | 0 | ReadTimeout: The read operation timed out |
| B | Desenvolvedor Pleno / Quiz / Fintech | 90.31 | None/None | NÃO | NÃO | NÃO | 0 | ReadTimeout: The read operation timed out |
| C | Gestor/Executivo / Resumo Executivo / Saude | 90.19 | None/None | NÃO | NÃO | NÃO | 0 | ReadTimeout: The read operation timed out |

- Latência: mediana 90.22 s, máxima 90.31 s (meta do projeto: 45 s por geração completa).
- JSON válido na 1ª tentativa: 0/3.
- Schema válido: 0/3. Chunks válidos: 0/3.
- Respostas HTTP 429 (limite de uso): 0.

## Embeddings

- **Dimensão do vetor: 768** (vai para `EMBEDDING_DIM` e `vector(N)`).
- Dimensão consistente em todos os textos: sim.
- Latência total de 9 textos: 3.84 s.
- Busca top-1 correta: 2/3.
  - [ERRO] esperado chunk-004, obtido chunk-003
  - [ok] esperado chunk-002, obtido chunk-002
  - [ok] esperado chunk-006, obtido chunk-006

## A preencher à mão para o ADR-0011

- Limites do plano gratuito (por minuto, por dia, tokens): ver painel do provedor.
- Qualidade em português dos 3 cenários (leitura humana): 
- Custo se passar do gratuito: 
