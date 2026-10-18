# 01 - Visão de produto

> **Projeto:** AdaptAI · **Evento:** Hackathon ONE G10 (Oracle Next Education & Alura)
> **Versão:** v2 · **Data:** 2026-10-17 · **Prazo:** primeira entrega em **24/11/2026**
> **Documentos relacionados:** [02 - Requisitos](./02%20-%20Requisitos.md) · [04 - Arquitetura](./04%20-%20Arquitetura.md) · [PRDs](./prd/README-PRD.md) · [ADRs](./adr/README-ADR.md)

---

## 1. Resumo

O **AdaptAI** é um sistema inteligente de adaptação e geração de conteúdo educacional. Ele ingere documentação técnica densa (PDF, Markdown ou texto bruto) e a transforma, em minutos, em **pacotes de estudo personalizados** (tutorial, flashcards, quiz, resumo executivo ou roteiro de aula) de acordo com o **perfil do destinatário**, o **nicho de aplicação** e o **nível de detalhe**.

Todo conteúdo é **ancorado na fonte original** por uma pipeline de RAG (chunking, embeddings e busca vetorial), para que o material gerado reflita fielmente a documentação e não alucine.

Sobre essa base, o AdaptAI acompanha o aluno: cada estudo gera **XP**, o usuário **evolui de nível** (Iniciante → Dev Júnior → Dev Pleno → Tech Lead → Arquiteto) e o conteúdo se adapta à sua jornada. Em uma frase: **"o Duolingo da documentação técnica"**.

## 2. Problema e dor do mercado

1. **Gargalo de produção.** Transformar um manual técnico em material didático consome semanas de especialistas e designers instrucionais, enquanto as documentações mudam na velocidade das atualizações de software.
2. **Um mesmo conteúdo para públicos muito diferentes.** Um manual de redes em nuvem precisa ser ensinado de formas distintas para quem dá os primeiros passos e para quem decide investimentos.
3. **Aprendizado não é estático.** O usuário evolui, mas resumos tradicionais de IA são genéricos e robóticos: o aluno perde o senso de progresso e o engajamento.
4. **Confiança.** Conteúdo gerado por IA sem ancoragem na fonte pode alucinar, o que é inaceitável em treinamento técnico.

## 3. Proposta de valor

| Para quem | Valor entregue |
|---|---|
| Equipes de EdTech e treinamento corporativo | Reduz a produção de material de semanas para minutos, com rastreabilidade até a fonte |
| Quem estuda | Conteúdo no nível, tom e formato certos, com analogias do cotidiano, e uma trilha visível de evolução |
| Lideranças e gestores | Resumos executivos sem jargão, com o contexto do setor |

## 4. Público e personas (ilustrativas)

- **Ana, transição de carreira (Iniciante).** Quer entender "do zero" conceitos como VCN, sem jargão. Precisa de analogias e de sensação de progresso.
- **Bruno, desenvolvedor pleno.** Quer validar rapidamente o que sabe, com quizzes que justificam as respostas e foco em decisões técnicas.
- **Carla, gestora (não técnica).** Precisa de um resumo executivo (TL;DR) com impacto de negócio no setor dela.

**Quem define o perfil:** o próprio usuário. Ele declara o nível no cadastro (RN-01) e pode alterar o perfil de saída em cada requisição (RN-02). O sistema **não decide a audiência**: apenas estima o nível do **documento** para o alerta de descompasso (RN-09, RN-18).

## 5. Diferenciais

1. **Trilha de Evolução gamificada.** XP, 5 níveis e **Teste de Nível** que valida o domínio antes da promoção. O sistema **sugere e alerta, nunca bloqueia**.
2. **Motor de Analogias.** Reconstrói conceitos complexos com analogias do cotidiano, adaptadas ao nicho. É *inspirado* na técnica de Feynman, mas é a IA quem explica. As analogias ficam **separadas do conteúdo ancorado** e são marcadas como não ancoradas, com mapeamento aos conceitos da fonte.
3. **Microlearning.** O estudo é dividido em blocos curtos com duração estimada.
4. **Fidelidade mensurável.** Score de ancoragem na fonte e rastreio de chunks em cada item gerado.

> **Nota de posicionamento:** os três primeiros diferenciais são **propostas da equipe** e não constam da lista de diferenciais do edital (que cita deploy na OCI Compute, multi-agente com LangGraph, quiz com avaliação em tempo real, multimodal e exportação multiformato). O edital não informa critérios de pontuação além do checklist de mínimos. Por isso o checklist vem **sempre antes** de qualquer diferencial.

## 6. Princípios de produto

1. **Fidelidade vem primeiro.** Nenhum diferencial pode comprometer a ancoragem na fonte.
2. **Sugere, não bloqueia.** O sistema orienta (alerta de descompasso de nível), mas o usuário decide.
3. **Evolução se prova.** XP e promoção dependem de validação, não apenas de cliques.
4. **Honestidade pedagógica.** Analogias declaram seu limite; conteúdo não ancorado é sempre identificado.
5. **MVP antes de evoluções.** O checklist da banca é concluído antes de qualquer diferencial.
6. **Custo zero.** Somente a camada Always Free da OCI.

## 7. Escopo

### 7.1 MVP base (inegociável)

- Ingestão de PDF, Markdown e texto bruto
- Pipeline RAG com chunking, embeddings e busca vetorial (`pgvector`, [ADR-0014](./adr/ADR-0014-pgvector-como-vector-store.md))
- Orquestração com LLM (LangGraph: recuperar, planejar, redigir, verificar) e saída JSON validada por Pydantic
- Perfil, formato, nicho e nível de detalhe parametrizáveis; 5 formatos de saída
- Metadados de aprendizado e avaliação de fidelidade
- Persistência de documentos e JSONs no OCI Object Storage, e de usuários, resultados e histórico no PostgreSQL ([ADR-0013](./adr/ADR-0013-postgresql-como-banco-de-leitura.md))
- API REST em FastAPI e front-end web separado, no mesmo monorepo
- Stack inteira executável com `docker compose up` ([ADR-0015](./adr/ADR-0015-docker-compose-e-backend-unico.md))
- Cadastro, login e logout simples (decisão de produto: **incluídos no MVP**, embora autenticação não conste do checklist do edital)
- 3 cenários de demonstração com o mesmo documento

### 7.2 Evoluções graduais (após o MVP base, validadas uma a uma)

1. Trilha de Evolução (XP, níveis, Teste de Nível, alerta de descompasso)
2. Motor de Analogias
3. Microlearning

### 7.3 Opcionais (se sobrar tempo)

- Exportação em Markdown e CSV compatível com Anki
- Deploy na OCI Compute (Always Free), reaproveitando o mesmo Compose
- Busca na web para enriquecer analogias (o schema já reserva `fontes_externas`)

### 7.4 Fora de escopo

Recuperação de senha, OAuth, ranking entre usuários, multimodal (diagramas), onboarding por estilos de aprendizagem, algoritmo de repetição espaçada (SM-2), Feynman reverso (o aluno explica e a IA avalia).

## 8. Metas e métricas de sucesso do hackathon

| Meta | Critério de sucesso |
|---|---|
| Checklist da banca | 100% dos itens obrigatórios funcionando |
| Fidelidade | `ancoragem_fonte_score` ≥ 0,80 nos 3 cenários de demo |
| Velocidade | Geração em até 45 s para documentos de até 20 páginas (meta, não SLA, ainda sem medição) |
| Evolução | Promoção de nível demonstrável em menos de 3 minutos no modo demo |
| Custo | Zero cobrança na OCI |
| Demonstração | 3 cenários distintos (perfil, formato e nicho) para o mesmo documento |
| Prazo | Primeira entrega em 24/11/2026 |

## 9. Rastreabilidade com o checklist da banca

| Requisito mínimo do edital | Onde é atendido |
|---|---|
| Ingestão de PDF, Markdown ou texto | RF-04 · Épico E1 |
| RAG com chunking, embeddings e busca vetorial | RF-05 · Épico E1 · ADR-0014 |
| Orquestração com LLM | RF-07 · Épico E2 · ADR-0004, ADR-0011 |
| Adaptar o mesmo conteúdo para 2+ perfis e 2+ formatos | RF-06, RF-07 · cenários de demo (Épico E10) |
| Saída JSON estruturada e interface ou API REST | RF-08, RF-20 · Épicos E2 e E5 · ADR-0001, ADR-0009 |
| Integração com OCI Object Storage | RF-11 · Épico E4 · ADR-0013 |
| 3 exemplos de execução | Épico E10 |
| Documentação com diagrama de arquitetura | `docs/04 - Arquitetura.md` e README |

Opcionais do edital contemplados: orquestração multi-agente com LangGraph (nós recuperador, redator e revisor; sem nó roteador), quiz com avaliação em tempo real (RF-13) e, se houver tempo, exportação multiformato e deploy na OCI Compute.

## 10. Roadmap resumido (até 24/11/2026)

| Período | Foco |
|---|---|
| Semana 1 (18 a 24/10) | Contrato JSON, Compose com Postgres e `pgvector`, esquema do banco, spikes de LLM e OCI, ambiente e wireframes |
| Semana 2 (25 a 31/10) | Login (back-end e telas), ingestão, chunking, embeddings e `pgvector`; telas de upload e render |
| Semana 3 (1 a 7/11) | Grafo LangGraph, fidelidade, persistência (banco e bucket), histórico. **Gate 1 em 7/11: MVP base completo e 3 cenários ensaiados** |
| Semana 4 (8 a 14/11) | Trilha de Evolução |
| Semana 5 (15 a 21/11) | Motor de Analogias e Microlearning. **Congelamento de funcionalidades em 20/11** |
| 22 a 24/11 | README, diagrama, ensaio da demo e buffer. **Entrega em 24/11** |

Detalhamento em [06 - Backlogs](./06%20-%20Backlogs.md).

## 11. Riscos de produto

| Risco | Impacto | Mitigação |
|---|---|---|
| Escopo maior que o prazo (5 semanas e 2 dias a partir de 18/10) | Alto | Entrega em camadas (ver 06 - Backlogs), cortando sempre pelo topo; gate em 7/11 |
| Integração com OCI deixada para o fim; conta ainda não criada | Alto | Conta, região e spike do Object Storage até o fim da semana 1 (ver risco R1 no backlog) |
| Equipe e horas por semana ainda indefinidas | Alto | Planejar como se uma pessoa tivesse de entregar o checklist; responsáveis em [08 - Mapas de Competências](./08%20-%20Mapas%20de%20Compet%C3%AAncias.md) |
| Score de fidelidade subjetivo | Médio | Método definido em ADR-0010; score sempre exibido com as fontes |
| Limites e latência de LLM gratuito | Médio | Limite de uma reescrita; cache de resultados; abstração de provedor |
| Documentos curtos dispensam a busca vetorial na geração | Médio | Registrar no README como a recuperação funciona; mitigação sugerida: ao menos um cenário com documento longo o bastante para exercitá-la |
| Analogia ensinar algo errado | Médio | Mapeamento obrigatório à fonte e campo `limite_da_analogia` |
| Gamificação sem substância | Médio | XP atrelado a validação e Teste de Nível |
| Diferenciais próprios sem pontuação conhecida | Médio | Checklist primeiro; perguntar aos organizadores se há rubrica para a fase final |

## 12. Glossário

- **Pacote educacional (adaptação):** JSON final com conteúdo adaptado, metadados, avaliação de qualidade e trilha.
- **Chunk:** trecho do documento original indexado no vector store.
- **Ancoragem:** grau em que o conteúdo gerado é sustentado pelos chunks recuperados.
- **Perfil de saída (`perfil_destinatario`):** público para o qual o conteúdo é escrito em uma requisição.
- **Nível do usuário:** posição do usuário na escada de evolução, um por usuário.
- **Nível do documento:** dificuldade estimada do documento, calculada na ingestão.
- **Teste de Nível:** quiz que valida o domínio do conteúdo do nível atual antes da promoção.
- **Descompasso:** diferença relevante entre o nível estimado do documento e o nível do usuário.
