# 06 - Backlogs

> **Versão:** v2 · **Data:** 2026-10-17 · **Horizonte:** 18/10 a 24/11/2026 (5 semanas e 2 dias)
> **Trilhas:** **BE** = back-end e IA (Python) · **FE** = front-end · **QA** = validação e demo
> **Prioridade:** **MVP** · **EVO** (evolução, só após o Gate 1 de 7/11) · **OPC** (opcional)
> **Relacionados:** [02 - Requisitos](./02%20-%20Requisitos.md) · [05 - Contrato de API](./05%20-%20Contrato%20de%20API.md) · [PRDs](./prd/README-PRD.md)

---

## 1. Como usar este backlog

- Cada história cita o **ID** (`US-xxx`) e os **critérios de aceite** objetivos. Responsáveis são atribuídos na planning de cada semana e **ainda não foram definidos**: quantas pessoas, quem faz o front e as horas por semana são dados em aberto (ver [08 - Mapas de Competências](./08%20-%20Mapas%20de%20Compet%C3%AAncias.md)).
- A ordem respeita a decisão de produto: **primeiro o MVP base, depois as evoluções**, validando cada evolução antes de seguir para a próxima.
- **Login é MVP e entra na semana 2** (decisão de produto). O back-end de login depende só do banco e das migrações (US-007 e US-008), não do RAG nem do LLM. Nenhum usuário fixo de desenvolvimento é usado após a semana 2.
- **Ordem de corte proposta (a confirmar pela equipe):** se o cronograma apertar, corta-se de cima para baixo na pilha abaixo; nunca o checklist da banca.

  | Camada | Conteúdo |
  |---|---|
  | 1 (nunca cortar) | Checklist da banca, via API |
  | 2 | Front-end, login, banco e histórico |
  | 3 | Trilha de Evolução |
  | 4 (corta primeiro) | Analogias e Microlearning; depois opcionais (exportação, deploy na VM) |

### Definição de pronto (DoD)

1. Critérios de aceite atendidos e demonstrados.
2. Código revisado em PR (ao menos 1 aprovação) e mergeado na `main`.
3. Testes das regras puras passando; lint sem erros.
4. Contrato (schemas e OpenAPI) atualizado, se aplicável.
5. Mudança de esquema acompanhada de **migração Alembic** no mesmo PR.
6. Nenhum segredo versionado e nenhum recurso fora da camada Always Free.
7. Documentação afetada atualizada (`docs/`, ADR ou README).

### Definição de preparado (DoR)

História com critérios de aceite claros, dependências identificadas e contrato (ou mock) disponível para a outra trilha.

## 2. Cronograma e gates

Datas: semanas começam no domingo. A primeira entrega é em **24/11/2026**, seguida de seleção e de uma fase final (data a confirmar com os organizadores; o dia 26/11 foi citado).

| Semana | Back-end e IA | Front-end | Gate |
|---|---|---|---|
| 1 (18 a 24/10) | Contrato, Compose com Postgres e `pgvector`, esquema e migrações, spike do LLM, spike da OCI, ambiente e CI | Wireframes, setup e mocks (depende do ADR-0012) | Contrato `1.0` publicado; `docker compose up` sobe a stack; spike do LLM concluído; spike da OCI concluído **ou risco escalado** |
| 2 (25 a 31/10) | **Login e isolamento por usuário**, ingestão, chunking, embeddings, `pgvector`, `POST /documentos` | Telas de login e cadastro, upload e parâmetros, render de Flashcards e Quiz | RAG recuperando bons chunks do documento de exemplo; login funcionando de ponta a ponta |
| 3 (1 a 7/11) | Grafo, fidelidade, persistência no banco e no bucket, `POST /adaptacoes`, histórico | Render dos 5 formatos, histórico, erros | **GATE 1 (7/11): MVP base completo e 3 cenários ensaiados** |
| 4 (8 a 14/11) | Trilha de Evolução (XP, perfil, Teste de Nível, descompasso) | Perfil, barra de nível, teste de nível | Promoção demonstrada no modo demo |
| 5 (15 a 21/11) | Motor de Analogias e Microlearning | Render de analogias e blocos; polimento | **GATE 2 (20/11): congelamento de funcionalidades** |
| Final (22 a 24/11) | README, diagrama, ensaio da demo, buffer, opcionais | Polimento e correção de bugs | Checklist final da banca; **entrega em 24/11** |

**Contingência:** a semana 3 continua a mais carregada (grafo, fidelidade, dupla persistência, 5 formatos). Como o login foi para a semana 2, ele deixou de ser a válvula de escape. Se a semana 3 estourar, a ordem é: opcionais primeiro, depois o que já está listado como camada 4, e o checklist da banca nunca é cortado.

**Aviso de capacidade:** o plano assume que a equipe consegue cumprir as semanas como escritas. Sem o número de pessoas e as horas por semana, isso é uma **hipótese**. Planeje como se uma pessoa precisasse entregar o checklist da banca de ponta a ponta.

### Gate 1 (7/11): critérios

- [ ] Ingestão de PDF, Markdown e texto funcionando
- [ ] RAG com chunking, embeddings e busca vetorial (`pgvector`)
- [ ] Geração nos 5 formatos com JSON validado por Pydantic
- [ ] Mesmo documento adaptado para 2+ perfis e 2+ formatos
- [ ] Persistência no OCI Object Storage (originais e JSONs) e no banco (resultado e histórico)
- [ ] Front-end consumindo a API, com login simples
- [ ] `docker compose up` sobe a stack do zero em outra máquina
- [ ] 3 cenários de demo executando de ponta a ponta

## 3. Cenários de demonstração (US-090)

Documento base: *Introdução à Arquitetura de Redes VCN na OCI* (exemplo do edital) e, para o terceiro cenário, um documento real adicional.

> **Em aberto:** o edital e a Visão de produto pedem 3 cenários para o **mesmo** documento, mas este backlog previa um documento adicional no terceiro. Definir um dos dois antes da semana 3. Recomendação: o mesmo documento nos três, mais **um documento longo** (acima de ~12 chunks) em pelo menos um cenário, para a recuperação vetorial ser de fato exercitada (`chunks_utilizados`).

| Cenário | Perfil | Formato | Nicho | O que demonstra |
|---|---|---|---|---|
| A | Iniciante | Flashcards | Geral | Linguagem acessível; analogias e microlearning (após semana 5) |
| B | Desenvolvedor Pleno | Quiz | Fintech | Quiz com feedback, XP e Teste de Nível |
| C | Gestor/Executivo | Resumo Executivo | Saúde | Sem jargão e foco em impacto de negócio |
| D (opcional) | Arquiteto | Tutorial | E-commerce | Profundidade técnica no mesmo documento |

## 4. Épicos e histórias

### E0 · Fundação

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-001 | Estrutura do repositório e ambiente | BE | 1 | Estrutura conforme `04 - Arquitetura`; `.env.example`; `.gitignore` cobre `.env` e chaves; a API sobe e responde `GET /health` seguindo o README |
| US-002 | Contrato inicial (schemas e OpenAPI) | BE | 1 | Schemas de requisição e resposta da seção 5 do contrato; `/openapi.json` publicado; `versao_schema = "1.0"`; `analogias` e `microlearning` no nível superior |
| US-003 | Mocks do contrato para o front | FE | 1 | Front roda contra mock com o exemplo completo do contrato; tipos gerados do OpenAPI |
| US-004 | Wireframes das 5 telas | FE | 1 | Login/cadastro, upload e parâmetros, resultado, histórico e perfil/nível desenhados e acordados com o back |
| US-005 | CI básico | BE | 1 | Pipeline executa lint e testes em cada PR |
| US-006 | Spike do OCI Object Storage | BE | 1 | **Pré-requisito: conta OCI com região principal definida.** Meio dia no máximo. Bucket Always Free criado; upload, download e listagem por prefixo funcionando via SDK; nenhum serviço pago habilitado; resultado documentado. Se a conta não puder ser criada na semana 1, registrar o bloqueio e escalar |
| US-007 | Docker Compose da stack | BE | 1 | `docker compose up` sobe `db` (PostgreSQL com `pgvector`), `backend` e `frontend` do zero; volume nomeado para o banco; banco não exposto fora da rede do Compose; imagem confirmada com `pgvector` (e com build para arm64, se for usar a VM Arm) |
| US-008 | Esquema do banco e migrações | BE | 1 | Tabelas da seção 7 do modelo de domínio criadas por **Alembic**; e-mail único; teste de integração cria e desfaz a migração; teste de gravação e leitura de `JSONB` e de `vector`; ORM e biblioteca de acesso ao `pgvector` decididos |
| US-009 | Spike do LLM e embeddings (ADR-0011) | BE | 1 | Provedor padrão e reserva testados nos 3 cenários; limites e latência medidos; modelo de embeddings escolhido e a dimensão registrada; ADR-0011 passa a `Aceito` |

### E1 · Ingestão e RAG (RF-04, RF-05)

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-010 | Extração de texto de PDF, MD e TXT | BE | 2 | PDF com texto, MD e texto bruto retornam texto normalizado; PDF sem texto retorna `DOCUMENTO_SEM_TEXTO`; acima de 10 MB retorna 413; tipo inválido retorna 415 |
| US-011 | Chunking determinístico | BE | 2 | Mesmo documento gera os mesmos `chunk_id`; tamanho e sobreposição configuráveis; teste unitário |
| US-012 | Embeddings e indexação no `pgvector` | BE | 2 | Linhas em `chunks` com `embedding`; consultas sempre filtradas por documento do usuário; 3 perguntas de teste sobre o documento de exemplo recuperam os chunks esperados; reindexar não duplica |
| US-013 | Reindexação a partir do bucket | BE | 3 | Apagando as linhas de `chunks` de um documento, o índice é recriado a partir de `documentos/` no bucket e as consultas voltam a funcionar |
| US-014 | `POST /documentos` | BE | 2 | Aceita arquivo ou texto; retorna `chunks_indexados`, `nivel_documento_estimado` (estimado na ingestão, `null` se o LLM falhar sem derrubar a requisição) e `status_upload`; deduplica por hash por usuário; usa o usuário autenticado |

### E2 · Orquestração e geração (RF-06, RF-07, RF-08)

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-020 | Abstração `LLMProvider` e provedor padrão | BE | 2 | Troca de provedor por variável de ambiente; LLM falso disponível para testes |
| US-021 | Grafo mínimo: recuperar, planejar, redigir, finalizar | BE | 3 | Gera Flashcards válidos para o documento de exemplo; saída validada por Pydantic |
| US-022 | Prompts e few-shots para os 5 formatos e 6 perfis | BE | 3 | Os 5 formatos passam na validação de schema; diferença perceptível entre Iniciante e Arquiteto no mesmo documento (revisão manual) |
| US-023 | Nicho e nível de detalhe nos prompts | BE | 3 | Mudar o nicho altera exemplos e vocabulário; mudar o nível de detalhe altera a profundidade |
| US-024 | `POST /adaptacoes` compatível com o edital | BE | 3 | Aceita o exemplo de requisição do edital; erros mapeados conforme contrato; `incluir_gabarito` implementado |
| US-025 | Nova tentativa em saída inválida | BE | 3 | Falha de parsing dispara 1 nova tentativa; persistindo, retorna `VALIDACAO_FALHOU` ou erro amigável |

### E3 · Fidelidade e metadados (RF-09, RF-10)

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-030 | Metadados de aprendizado | BE | 3 | `conceitos_chave`, `pre_requisitos` e `tempo_estimado_estudo_minutos` presentes e coerentes |
| US-031 | Verificação de fidelidade e uma reescrita | BE | 3 | `ancoragem_fonte_score` entre 0 e 1, calculado só sobre afirmações factuais (RN-19); abaixo de 0,80 dispara 1 reescrita; nos 3 cenários o score é ≥ 0,80 ou a observação registra o motivo |
| US-032 | Rastreio de `fontes_chunks` por item | BE | 3 | Todo item de conteúdo cita ao menos 1 chunk existente |
| US-033 | Clareza pedagógica | BE | 3 | `clareza_pedagogica` retornada como Alta, Média ou Baixa com observações |

### E4 · Persistência: banco e OCI (RF-11, RF-12)

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-035 | `StoragePort`, `OCIObjectStorage` e `LocalFileStorage` | BE | 3 | Mesma suíte de testes passa nas duas implementações; troca por `STORAGE_BACKEND` |
| US-036 | Persistir o resultado no banco e enviar original e JSON ao bucket | BE | 3 | Transação grava resultado, XP e perfil com `status_upload = pendente`; em seguida, envio ao bucket e atualização para `concluido` ou `falha`; falha no bucket **não perde o resultado**; resposta traz `armazenamento_oci` com o `status_upload` final |
| US-037 | Histórico de documentos e adaptações, lido do banco | BE e FE | 3 | Listar e reabrir adaptações do próprio usuário sem tocar no bucket; recursos de outro usuário retornam 404 |
| US-038 | Reenvio de pendentes e backup do banco | BE | 3 | Script idempotente reenvia os objetos com `status_upload` pendente ou com falha; `pg_dump` periódico enviado a `backups/postgres/`; restauração testada uma vez |

### E5 · API e front-end (RF-19, RF-20, RF-21)

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-050 | Tratamento padronizado de erros | BE | 3 | Todos os códigos da seção 8 do contrato, inclusive `BANCO_INDISPONIVEL`; sem stack trace na resposta; `request_id` presente |
| US-051 | Tela de upload e parâmetros | FE | 2 | Envia arquivo ou texto e escolhe perfil, formato, nicho e detalhe; mostra carregamento |
| US-052 | Render dos 5 formatos | FE | 2 e 3 | Flashcards e Quiz na semana 2; Tutorial, Resumo Executivo e Roteiro na semana 3; tolera campos `null` |
| US-053 | Tela de histórico | FE | 3 | Lista e reabre adaptações anteriores |
| US-054 | Erros amigáveis, carregamento e estados vazios | FE | 3 | Cada código de erro tem mensagem em PT-BR; sem telas em branco; `status_upload = falha` aparece como aviso, não como erro |
| US-055 | Polimento e responsividade | FE | 5 | Layout funcional em desktop e celular |
| US-056 | Exportação em Markdown e CSV Anki | BE e FE | Final | Download de Markdown e CSV importável no Anki (**OPC**) |

### E6 · Autenticação (RF-01, RF-02, RF-03) · **MVP · semana 2**

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-040 | Cadastro com nível declarado | BE | 2 | E-mail único (409 se repetido, garantido pelo banco); senha mínima de 8 caracteres; hash bcrypt; cria a linha do perfil de evolução com XP zero |
| US-041 | Login, JWT e dependência de autenticação | BE | 2 | Token com expiração; rotas protegidas retornam 401 sem token válido |
| US-042 | Logout | BE e FE | 2 | `204`; front descarta o token e redireciona ao login |
| US-043 | Telas de cadastro e login | FE | 2 | Fluxo completo com validação e mensagens de erro |
| US-044 | Isolamento por usuário | BE | 2 | Acesso a recurso de outro usuário retorna 404 (teste automatizado, na consulta ao banco) |
| US-045 | Seed do usuário de demonstração | BE | 2 | Script cria o usuário demo e está descrito no README |

### E7 · Trilha de Evolução (RF-13 a RF-16) · **EVO · semana 4**

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-060 | Regras puras de XP e nível | BE | 4 | RN-03, RN-04 e RN-05 cobertas por testes: teto diário, acerto pontuado uma vez, limiares e nível máximo |
| US-061 | Perfil no banco e `GET /perfil` | BE | 4 | Linha de `perfis_evolucao` criada no cadastro e atualizada na mesma transação de cada fluxo (RNF-14); linha travada ao aplicar XP; teste de dois pedidos simultâneos não duplica XP |
| US-062 | XP de geração em `POST /adaptacoes` | BE | 4 | +10 XP até 3 gerações por dia; `xp_ganho_nesta_sessao` correto |
| US-063 | Resposta de quiz com feedback e XP | BE e FE | 4 | +5 XP por acerto, uma vez por pergunta (índice único); feedback com justificativa; gabarito validado no servidor |
| US-064 | Alerta de descompasso | BE e FE | 4 | `nivel_documento_estimado` (calculado na ingestão, RN-18) retornado; alerta quando a diferença é de 2 degraus ou mais; sem alerta quando o nível é `null`; o front mostra o aviso sem bloquear |
| US-065 | Teste de Nível | BE | 4 | Disponível ao atingir o limiar; 5 a 8 perguntas dos conceitos do nível; aprovação com percentual ≥ 70%; reprovação mostra conceitos fracos e permite nova tentativa com perguntas diferentes; `CONCEITOS_INSUFICIENTES` com menos de 3 conceitos |
| US-066 | Telas de perfil, nível e teste | FE | 4 | Barra de progresso, nível atual, teste de nível e feedback de promoção |
| US-067 | Modo demo | BE | 4 | `AdaptAI_MODO_DEMO=true` aplica fator 0,1 aos limiares |
| US-068 | Validação da evolução ponta a ponta | QA | 4 | Promoção demonstrada no modo demo em menos de 3 minutos |

### E8 · Motor de Analogias (RF-17) · **EVO · semana 5**

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-070 | Nó `enriquecer` com analogias | BE | 5 | Até 3 analogias por pacote, cada uma com mapeamento, `limite_da_analogia`, `ancorada_na_fonte = false` e `conceito_ancorado_em` |
| US-071 | Analogias por nicho | BE | 5 | Few-shots para Geral, Fintech, Saúde e E-commerce; analogias coerentes com o nicho (revisão manual) |
| US-072 | `fidelidade_analogias_score` | BE | 5 | Score calculado a partir da validade do mapeamento; analogias fora do score principal |
| US-073 | Render de analogias | FE | 5 | Destaque visual "analogia, não vem da fonte"; limite da analogia visível |
| US-074 | Campo `fontes_externas` reservado | BE | 5 | Presente e vazio; documentado para a evolução com busca na web |

### E9 · Microlearning (RF-18) · **EVO · semana 5**

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-080 | Blocos de microlearning | BE | 5 | De 2 a 5 blocos de 2 a 5 minutos; soma igual ao tempo estimado; cada bloco referencia itens existentes |
| US-081 | Render dos blocos | FE | 5 | Blocos em sequência com duração; sem cronômetro nesta versão |

### E10 · Documentação e demo

| ID | História | Trilha | Sem. | Critérios de aceite |
|---|---|---|---|---|
| US-090 | Cenários de demonstração | QA | 3, 5 e Final | Versão preliminar na semana 3, final na 5 e ensaio na semana final; scores e JSONs salvos como evidência; ao menos um cenário exercita a recuperação vetorial |
| US-091 | README | todos | Final | Arquitetura, diagrama RAG e agentes (descrevendo o que existe, sem inflar "multi-agente"), guia de instalação com `docker compose up`, seed e variáveis de ambiente |
| US-092 | Roteiro de apresentação | todos | Final | Roteiro de 5 minutos ensaiado com os 3 cenários e a trilha de evolução |
| US-093 | Deploy na OCI Compute | BE | Final | **OPC.** O mesmo Compose em VM Always Free. Antes: medir a memória do conjunto, confirmar a capacidade da região e o suporte a arm64. A demonstração principal **não depende** desta história |
| US-094 | Checklist final da banca | todos | Final | Todos os itens do edital marcados com evidência |

## 5. Riscos que afetam o backlog

| Risco | Efeito | Resposta |
|---|---|---|
| R1. Conta OCI ainda não criada | Spike e integração do requisito obrigatório descobertos tarde (cadastro com cartão, verificação, região que não pode ser trocada) | Criar a conta, escolher a região e fazer o spike de meio dia na semana 1. Se o cartão falhar, procurar alternativa já na semana 1 |
| R2. Equipe e horas por semana indefinidas | Front e trilhas paralelas sem dono | Responsáveis definidos na planning da semana 1; plano mínimo executável por uma pessoa |
| R3. Prazo de 37 dias com escopo grande | Camadas 3 e 4 não cabem | Entrega em camadas, corte de cima para baixo, congelamento em 20/11 |
| R4. Semana 3 sobrecarregada | MVP base atrasa | Login movido para a semana 2; corte de opcionais, nunca do checklist |
| R5. Fidelidade abaixo de 0,80 nos cenários | Demo fraca | Ajustar chunking, prompts e juiz na semana 3; registrar observação honesta |
| R6. Limite do LLM gratuito durante a demo | Demo falha | Resultados dos 3 cenários pré-gerados e salvos (banco e bucket) como plano B; provedor reserva |
| R7. Front atrasado | Demo sem interface | O Swagger (`/docs`) cumpre "API REST operacional" |
| R8. Banco e bucket divergem | Histórico incompleto no bucket | `status_upload`, reenvio idempotente (US-038) e reindexação (US-013) |
| R9. Estado do banco perdido | Usuários e XP perdidos | Volume nomeado e `pg_dump` periódico para o bucket (US-038) |
| R10. VM Always Free indisponível ou recuperada | Deploy opcional falha | A demonstração principal roda local; VM é bônus |
| R11. Busca vetorial nunca exercitada com documentos curtos | Item do checklist só comprovado pelo código | Cenário com documento longo; `chunks_utilizados` visível |
| R12. Diferenciais próprios sem pontuação conhecida | Esforço sem retorno na avaliação | Checklist primeiro; perguntar aos organizadores se há rubrica para a fase final |
