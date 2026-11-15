# Spike LLM — gemini / gemini-3.5-flash-lite

Embeddings: `gemini-embedding-001`. Repetições: 5.

## Geração (3 cenários, mesmo documento)

| Cenário | Perfil / formato / nicho | Latência (s) | Tokens ent./saída | JSON | Schema | Chunks | Itens | Erro |
|---|---|---|---|---|---|---|---|---|
| A | Iniciante / Flashcards / Geral | 5.43 | 591/692 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 2.92 | 623/830 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 2.43 | 598/698 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 4.57 | 591/655 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 3.38 | 623/1132 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 2.81 | 598/663 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 4.05 | 591/656 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 10.47 | 623/970 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 9.33 | 598/767 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 6.54 | 591/717 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 10.65 | 623/1294 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 6.73 | 598/724 | sim | sim | sim | 4 | - |
| A | Iniciante / Flashcards / Geral | 7.23 | 591/634 | sim | sim | sim | 4 | - |
| B | Desenvolvedor Pleno / Quiz / Fintech | 6.21 | 623/1065 | sim | sim | sim | 4 | - |
| C | Gestor/Executivo / Resumo Executivo / Saude | 6.19 | 598/668 | sim | sim | sim | 4 | - |

- Latência: mediana 6.19 s, máxima 10.65 s (meta do projeto: 45 s por geração completa).
- JSON válido na 1ª tentativa: 15/15.
- Schema válido: 15/15. Chunks válidos: 15/15.
- Respostas HTTP 429 (limite de uso): 0.

## Embeddings

- **Dimensão do vetor: 768** (vai para `EMBEDDING_DIM` e `vector(N)`).
- Dimensão consistente em todos os textos: sim.
- Latência total de 9 textos: 31.39 s.
- Busca top-1 correta: 2/3.
  - [ERRO] esperado chunk-004, obtido chunk-003
  - [ok] esperado chunk-002, obtido chunk-002
  - [ok] esperado chunk-006, obtido chunk-006

## A preencher à mão para o ADR-0011

- Limites do plano gratuito (por minuto, por dia, tokens): ver painel do provedor.
- Qualidade em português dos 3 cenários (leitura humana): 
- Custo se passar do gratuito: 
