# Spike LLM — gemini / gemini-3.7-flash

Embeddings: `gemini-embedding-001`. Repetições: 1.

## Geração (3 cenários, mesmo documento)

| Cenário | Perfil / formato / nicho | Latência (s) | Tokens ent./saída | JSON | Schema | Chunks | Itens | Erro |
|---|---|---|---|---|---|---|---|---|
| A | Iniciante / Flashcards / Geral | 60.15 | None/None | NÃO | NÃO | NÃO | 0 | ReadTimeout: The read operation timed out |
| B | Desenvolvedor Pleno / Quiz / Fintech | 23.31 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| C | Gestor/Executivo / Resumo Executivo / Saude | 50.24 | 598/835 | sim | sim | sim | 4 | - |

- Latência: mediana 50.24 s, máxima 60.15 s (meta do projeto: 45 s por geração completa).
- JSON válido na 1ª tentativa: 1/3.
- Schema válido: 1/3. Chunks válidos: 1/3.
- Respostas HTTP 429 (limite de uso): 0.

## Embeddings

- **Dimensão do vetor: 768** (vai para `EMBEDDING_DIM` e `vector(N)`).
- Dimensão consistente em todos os textos: sim.
- Latência total de 9 textos: 3.8 s.
- Busca top-1 correta: 2/3.
  - [ERRO] esperado chunk-004, obtido chunk-003
  - [ok] esperado chunk-002, obtido chunk-002
  - [ok] esperado chunk-006, obtido chunk-006

## A preencher à mão para o ADR-0011

- Limites do plano gratuito (por minuto, por dia, tokens): ver painel do provedor.
- Qualidade em português dos 3 cenários (leitura humana): 
- Custo se passar do gratuito: 
