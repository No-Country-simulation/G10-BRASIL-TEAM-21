# PRD-001 — Adaptação de conteúdo educacional (MVP base)

- **Status:** Aprovado (revisado em 2026-10-17)
- **Prioridade:** MVP (inegociável)
- **Requisitos relacionados:** RF-04 a RF-12, RF-19, RF-20 · RN-02, RN-11, RN-12, RN-17 a RN-19 · RNF-03 a RNF-08, RNF-14
- **Épicos:** E1, E2, E3, E4, E5

## 1. Resumo

O usuário envia um documento técnico (PDF, Markdown ou texto) e escolhe **perfil do destinatário, formato de saída, nicho e nível de detalhe**. O sistema indexa o documento, gera um pacote educacional **ancorado na fonte** e devolve um JSON estruturado. O resultado fica no banco (para o histórico e a leitura do front-end) e os arquivos, no OCI Object Storage.

## 2. Problema

Criar material didático a partir de documentação densa leva semanas e raramente se adapta a públicos diferentes. Conteúdo gerado por IA sem ancoragem pode alucinar.

## 3. Objetivos e não objetivos

**Objetivos**
1. Transformar um documento em pacotes de estudo em até 45 s (meta ainda sem medição, documentos de até 20 páginas).
2. Adaptar o **mesmo** documento para perfis e formatos diferentes.
3. Garantir fidelidade mensurável (`ancoragem_fonte_score` ≥ 0,80) e rastreável (`fontes_chunks`).
4. Guardar resultados e histórico no banco, e originais e JSONs no OCI Object Storage, sem perder o resultado se a nuvem falhar (RN-17).

**Não objetivos (neste PRD)**
Trilha de evolução, analogias, microlearning (PRD-003 a PRD-005); busca na web; edição manual do conteúdo gerado; multimodal.

## 4. Usuários e cenários

| Usuário | Cenário |
|---|---|
| Iniciante em transição de carreira | Envia o manual de VCN e recebe flashcards sem jargão |
| Desenvolvedor pleno | Recebe um quiz com justificativas sobre o mesmo manual |
| Gestor | Recebe um resumo executivo com impacto no setor |

Em todos os casos, **o usuário define o perfil**: ele vem preenchido com o nível declarado no cadastro e é editável a cada requisição (RN-02). O sistema não decide a audiência pelo conteúdo do documento.

## 5. Requisitos e regras

### 5.1 Entrada

| Campo | Regra |
|---|---|
| Documento | PDF, MD ou TXT, até 10 MB, ou texto bruto colado. PDF digitalizado (sem texto) é rejeitado com mensagem clara |
| `perfil_destinatario` | Define vocabulário e profundidade. Vem preenchido com o nível do usuário, editável (RN-02) |
| `formato_saida` | Um dos 5 formatos |
| `nicho_setor` | Define exemplos e vocabulário do setor |
| `nivel_detalhe` | Define a extensão e a profundidade |

### 5.2 Formatos de saída (referência de tamanho)

| Formato | O que entrega |
|---|---|
| Flashcards | De 8 a 12 cartões (frente, verso, dica didática) |
| Quiz | De 5 a 8 perguntas com 4 alternativas, resposta correta e justificativa |
| Tutorial | De 5 a 10 passos com instrução e exemplo |
| Resumo Executivo | Até 5 tópicos com resumo e impacto de negócio |
| Roteiro de Aula | De 3 a 6 blocos com fala, duração e recurso visual opcional |

A quantidade varia com o `nivel_detalhe` e o tamanho do documento.

### 5.3 Processamento

1. **Ingestão (uma vez por documento):** extrair, normalizar, segmentar (chunking), gerar embeddings e indexar no `pgvector` (ADR-0014). Estimar `nivel_documento_estimado` e guardá-lo no banco (RN-18); se o LLM falhar nessa etapa, o campo fica `null` e a ingestão **não** falha.
2. Executar o grafo: recuperar, planejar, redigir, verificar fidelidade e finalizar (ADR-0004).
3. Se `ancoragem_fonte_score` < 0,80, reescrever **uma vez** (RN-12, ADR-0010). O juiz avalia só afirmações factuais; linguagem figurada é permitida (RN-19).
4. Validar o JSON com Pydantic; em falha, **uma** nova tentativa.
5. **Persistir (RN-17):** gravar o resultado no banco com `status_upload = pendente` (na mesma transação do XP, quando houver); enviar o original e o JSON ao bucket; atualizar `status_upload` e devolver `armazenamento_oci`. Falha no bucket **não derruba** a requisição.

### 5.4 Saída

Contrato em [05 - Contrato de API](../05%20-%20Contrato%20de%20API.md). Inclui `metadados` (conceitos-chave, pré-requisitos, tempo estimado), `conteudo_adaptado` com `fontes_chunks` por item (RN-11), `avaliacao_qualidade` e `armazenamento_oci`. Os campos `analogias` e `microlearning` (EVO) são de **nível superior**, ao lado de `conteudo_adaptado`.

### 5.5 Erros amigáveis

Mensagens em PT-BR e sem stack trace para: arquivo inválido ou grande demais, PDF sem texto, LLM indisponível, banco indisponível e tempo esgotado. Falha no envio ao bucket **não é erro**: aparece como `status_upload = falha`, com o resultado já salvo.

### 5.6 Segurança do conteúdo

O texto do documento é **dado não confiável** (RNF-03). Instruções embutidas nele não podem alterar o comportamento do sistema.

## 6. Critérios de aceite

1. O exemplo de requisição do edital é aceito e retorna uma resposta válida.
2. O **mesmo** documento gera Flashcards para Iniciante e Quiz para Desenvolvedor Pleno, com diferença perceptível de linguagem e profundidade.
3. Os 5 formatos passam na validação de schema.
4. Todo item de conteúdo cita ao menos um chunk existente.
5. `ancoragem_fonte_score` ≥ 0,80 nos 3 cenários de demonstração, ou a observação explica o motivo.
6. O resultado aparece no histórico (lido do banco). Original e JSON aparecem no bucket e a resposta traz `status_upload`.
7. Com o bucket indisponível, a adaptação **é entregue e salva**, com `status_upload = falha`, e o reenvio posterior a conclui.
8. Falhas retornam os códigos do contrato com mensagem amigável.
9. Um documento com instrução embutida ("ignore as regras anteriores") não muda o formato nem o comportamento da resposta.
10. Pelo menos um cenário usa um documento longo o bastante para a recuperação vetorial ser exercitada (`chunks_utilizados` visível).

## 7. Métricas de sucesso

| Métrica | Meta |
|---|---|
| Tempo de geração | Até 45 s (documentos de até 20 páginas); ainda sem medição |
| Fidelidade | ≥ 0,80 nos cenários de demonstração |
| Falhas de schema após nova tentativa | 0 nos 3 cenários |
| Cenários distintos executados | 3 ou mais |

## 8. Dependências e riscos

- Depende de: Compose e banco (US-007, US-008), OCI (US-006), provedor de LLM (ADR-0011), contrato (US-002) e login (E6, semana 2).
- **Riscos:** fidelidade abaixo do alvo, limite do LLM gratuito, qualidade da extração de PDF, divergência entre banco e bucket. Respostas em [06 - Backlogs](../06%20-%20Backlogs.md#5-riscos-que-afetam-o-backlog).

## 9. Perguntas em aberto

1. Documentos em **inglês**: a saída será sempre em PT-BR? *Proposta:* sim, documentos em PT-BR ou EN e saída em PT-BR.
2. Limite de páginas na demonstração, para controlar latência e custo de tokens.
3. Quantos itens exatos por formato e nível de detalhe (calibrar na semana 3).
