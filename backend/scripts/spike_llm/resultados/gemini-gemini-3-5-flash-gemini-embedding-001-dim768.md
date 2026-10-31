# Spike LLM — gemini / gemini-3.5-flash

Embeddings: `gemini-embedding-001`. Repetições: 5.

## Geração (3 cenários, mesmo documento)

| Cenário | Perfil / formato / nicho | Latência (s) | Tokens ent./saída | JSON | Schema | Chunks | Itens | Erro |
|---|---|---|---|---|---|---|---|---|
| A | Iniciante / Flashcards / Geral | 18.37 | 591/694 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 2.32 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| C | Gestor/Executivo / Resumo Executivo / Saude | 11.36 | 598/823 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 11.06 | 591/703 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 16.22 | 623/1249 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 6.73 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| A | Iniciante / Flashcards / Geral | 10.24 | 591/681 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 31.04 | 623/1448 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 17.12 | 598/795 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 4.73 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| B | Desenvolvedor Pleno / Quiz / Fintech | 0.94 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| C | Gestor/Executivo / Resumo Executivo / Saude | 12.22 | 598/773 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 1.9 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |
| B | Desenvolvedor Pleno / Quiz / Fintech | 17.85 | 623/1617 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 1.98 | None/None | NÃO | NÃO | NÃO | 0 | HTTP 503: {   "error": {     "code": 503,     "message": "This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.",     "status": "UNAVAILABLE"   } }  |

- Latência: mediana 11.06 s, máxima 31.04 s (meta do projeto: 45 s por geração completa).
- JSON válido na 1ª tentativa: 9/15.
- Schema válido: 9/15. Chunks válidos: 9/15.
- Respostas HTTP 429 (limite de uso): 0.

## Embeddings

- **Dimensão do vetor: 768** (vai para `EMBEDDING_DIM` e `vector(N)`).
- Dimensão consistente em todos os textos: sim.
- Latência total de 9 textos: 30.93 s.
- Busca top-1 correta: 2/3.
  - [ERRO] esperado chunk-004, obtido chunk-003
  - [ok] esperado chunk-002, obtido chunk-002
  - [ok] esperado chunk-006, obtido chunk-006

## A preencher à mão para o ADR-0011

- Limites do plano gratuito (por minuto, por dia, tokens): ver painel do provedor.
- Qualidade em português dos 3 cenários (leitura humana): 
- Custo se passar do gratuito: 
