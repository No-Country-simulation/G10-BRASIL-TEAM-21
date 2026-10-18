# 02 - Requisitos

> **Versão:** v2 · **Data:** 2026-10-17
> **Convenção de prioridade:** **MVP** (obrigatório para a banca) · **EVO** (evolução graduada após o gate de 7/11) · **OPC** (opcional, se sobrar tempo)
> **Épicos:** E0 Fundação · E1 Ingestão e RAG · E2 Orquestração e geração · E3 Fidelidade e metadados · E4 Persistência (banco e OCI) · E5 API e front-end · E6 Autenticação · E7 Trilha de evolução · E8 Motor de analogias · E9 Microlearning · E10 Documentação e demo

---

## 1. Requisitos funcionais

| ID | Requisito | Prioridade | Épico |
|---|---|---|---|
| RF-01 | Cadastro de usuário (nome, e-mail, senha, nível inicial declarado) | MVP | E6 |
| RF-02 | Login com e-mail e senha, retornando token de acesso | MVP | E6 |
| RF-03 | Logout (invalidação do token no cliente) | MVP | E6 |
| RF-04 | Upload e ingestão de documento técnico em PDF, Markdown ou texto bruto | MVP | E1 |
| RF-05 | Indexação RAG: chunking, embeddings e armazenamento no `pgvector` | MVP | E1 |
| RF-06 | Parametrização da adaptação: perfil do destinatário, formato de saída, nicho e nível de detalhe | MVP | E2 |
| RF-07 | Geração do pacote educacional nos 5 formatos: Tutorial, Flashcards, Quiz, Resumo Executivo e Roteiro de Aula | MVP | E2 |
| RF-08 | Saída em JSON estruturado, validada por schemas Pydantic de entrada e saída | MVP | E2 |
| RF-09 | Metadados de aprendizado: conceitos-chave, pré-requisitos e tempo estimado de estudo | MVP | E3 |
| RF-10 | Avaliação de qualidade: score de ancoragem na fonte e clareza pedagógica | MVP | E3 |
| RF-11 | Persistência no OCI Object Storage dos documentos originais e dos JSONs gerados | MVP | E4 |
| RF-12 | Histórico: listar e reabrir adaptações e documentos do usuário, lidos do banco | MVP | E4 |
| RF-13 | Responder quiz gerado com feedback explicativo imediato e concessão de XP | EVO | E7 |
| RF-14 | Perfil do usuário: nível, XP total, progresso e conceitos dominados | EVO | E7 |
| RF-15 | Alerta de descompasso entre o nível estimado do documento e o nível do usuário | EVO | E7 |
| RF-16 | Teste de Nível e promoção de nível | EVO | E7 |
| RF-17 | Motor de Analogias: analogias adaptadas ao nicho, com mapeamento e limite | EVO | E8 |
| RF-18 | Microlearning: divisão do estudo em blocos curtos com duração | EVO | E9 |
| RF-19 | Tratamento de exceções com mensagens de erro amigáveis em PT-BR | MVP | E5 |
| RF-20 | Interface web (front-end separado) para todos os fluxos acima | MVP | E5 |
| RF-21 | Exportação em Markdown e CSV compatível com Anki | OPC | E5 |

## 2. Requisitos não funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-01 | Custo | Usar exclusivamente a camada **Always Free** da OCI. Nenhum recurso que gere cobrança. O PostgreSQL roda em container e não consome serviço pago da OCI |
| RNF-02 | Segurança | Senhas com hash bcrypt, nunca em texto puro. Token JWT com expiração. Segredos apenas em variáveis de ambiente; **nunca versionar** credenciais da OCI, do banco ou chaves de LLM. |
| RNF-03 | Segurança | O conteúdo do documento é **dado não confiável**: instruções embutidas no texto não devem alterar o comportamento do sistema (delimitação no prompt e validação da saída). |
| RNF-04 | Segurança | Limite de tamanho (10 MB) e tipo (PDF, MD, TXT) no upload. CORS restrito à origem do front-end. O banco não é exposto fora da rede do Compose. |
| RNF-05 | Desempenho | Meta de até 45 s por geração para documentos de até 20 páginas. Ainda sem medição. |
| RNF-06 | Confiabilidade | Saída do LLM validada por Pydantic, com uma nova tentativa em caso de falha de parsing. |
| RNF-07 | Fidelidade | `ancoragem_fonte_score` mínimo de 0,80. Abaixo disso, o revisor reescreve uma vez (RN-12). |
| RNF-08 | Usabilidade | Interface e mensagens de erro em PT-BR, sem expor stack traces. |
| RNF-09 | Observabilidade | Logs estruturados com `request_id` e registro de latência e tokens por etapa do grafo. |
| RNF-10 | Manutenibilidade | Convenções de código e de Git conforme [07 - Convenções](./07%20-%20Conven%C3%A7%C3%B5es.md). |
| RNF-11 | Reprodutibilidade | README com guia de instalação e usuário de demonstração por script de seed. |
| RNF-12 | Compatibilidade | Contrato JSON estende, sem quebrar, o modelo de requisição e resposta do edital. |
| RNF-13 | Portabilidade | A stack inteira (banco, backend e front-end) sobe com `docker compose up` em ambiente local, com a mesma configuração usada na VM. |
| RNF-14 | Consistência | O resultado de uma adaptação e o XP correspondente são gravados em **uma única transação** no banco. A falha do envio ao bucket não perde o resultado (RN-17). |

## 3. Regras de negócio (v1 congeladas)

> As regras RN-01 a RN-16 são as congeladas em 13/10/2026 (RN-09 recebeu um ajuste de quando o nível do documento é estimado). **RN-17 a RN-19 foram acrescentadas em 17/10/2026**, após a decisão de adotar o PostgreSQL (ADR-0013). O título mantém "v1" para não quebrar os links de ADRs já aceitos.

| ID | Regra |
|---|---|
| RN-01 | O usuário informa seu **nível** no cadastro, entre 5 degraus: Iniciante, Desenvolvedor Júnior, Desenvolvedor Pleno, Tech Lead e Arquiteto. O nível é **um por usuário** (global). |
| RN-02 | O **perfil de saída** (`perfil_destinatario`) de cada requisição vem preenchido com o nível do usuário e pode ser alterado livremente. **Gestor/Executivo** é um perfil de saída fora da escada de níveis. |
| RN-03 | **XP por geração:** +10 XP por adaptação gerada, com teto de 3 gerações pontuáveis por dia (dia civil em America/Sao_Paulo). |
| RN-04 | **XP por validação:** +5 XP por pergunta de quiz respondida corretamente, uma vez por pergunta e por adaptação. Em v1 **só o formato Quiz** oferece validação; o Teste de Nível não concede XP (ele promove o nível). |
| RN-05 | **Limiares de XP acumulado:** 100 (Iniciante → Júnior), 250 (Júnior → Pleno), 450 (Pleno → Tech Lead) e 700 (Tech Lead → Arquiteto). Valores em arquivo de configuração e **ponto de partida para calibragem**. O nível Arquiteto é o máximo. |
| RN-06 | Ao atingir o limiar, o usuário passa a ter o **Teste de Nível** disponível: quiz simples sobre os conceitos do nível atual. O XP continua acumulando. |
| RN-07 | **Aprovação:** percentual de domínio no Teste de Nível maior ou igual a 70% (`limiar_aprovacao`). Aprovado, o nível sobe e o XP total é preservado. Reprovado, o sistema mostra os conceitos fracos e permite nova tentativa com perguntas diferentes. |
| RN-08 | O sistema **sugere e alerta, nunca bloqueia**: o usuário pode gerar conteúdo de qualquer nível a qualquer momento. |
| RN-09 | **Alerta de descompasso:** se a diferença entre o `nivel_documento_estimado` do documento e o nível do usuário for de 2 degraus ou mais, `alerta_descompasso = true`. O limite é configurável. |
| RN-10 | **Analogias** são conteúdo externo à fonte: sempre `ancorada_na_fonte = false`, com mapeamento a conceitos da fonte (`conceito_ancorado_em`) e `limite_da_analogia`. Máximo de 3 analogias por pacote. |
| RN-11 | O **conteúdo ancorado** deve indicar os chunks de origem (`fontes_chunks`). |
| RN-12 | Se `ancoragem_fonte_score` < 0,80, o revisor reescreve o conteúdo **uma vez**. Se persistir abaixo, o pacote é entregue com aviso em `avaliacao_qualidade.observacoes`. |
| RN-13 | A **busca na web** está adiada, para analogias e para qualquer conteúdo. O schema reserva `fontes_externas` (vazio no MVP) e qualquer fonte externa futura deve trazer URL e ficar em campo separado, fora do score de ancoragem. |
| RN-14 | Senhas nunca são armazenadas em texto puro. Não há recuperação de senha nem login social. |
| RN-15 | Só se usam recursos Always Free da OCI. |
| RN-16 | **Modo demo** (variável de ambiente): multiplica os limiares de XP por 0,1 para demonstrar a promoção de nível em minutos. |
| RN-17 | **Persistência dupla:** o resultado é gravado primeiro no banco, com `status_upload = pendente`, em transação com o XP. Em seguida, o original e o JSON são enviados ao bucket, e `status_upload` passa a `concluido` ou `falha`. O banco é a fonte de leitura do front-end; o bucket é arquivo e evidência. Pendências são reenviadas por script idempotente. |
| RN-18 | O **nível do documento** (`nivel_documento_estimado`) é estimado **uma vez, na ingestão**, e guardado no banco. As adaptações do mesmo documento o reutilizam. |
| RN-19 | **Linguagem figurada:** a introdução e as dicas do conteúdo ancorado podem usar metáforas, mas sem afirmar fatos técnicos novos. O juiz de fidelidade avalia **somente afirmações factuais**. Analogias com mapeamento ficam exclusivamente em `analogias`. |

## 4. Premissas e restrições

- Monorepo único: back-end em **Python** com FastAPI e front-end **separado**, sem Streamlit (ADR-0001, ADR-0002 e ADR-0015).
- LLM e modelo de embeddings: proposta no ADR-0011, a validar pela equipe.
- Framework do front-end: React com Vite ([ADR-0012](./adr/ADR-0012-framework-do-front-end.md)); TypeScript ou JavaScript a registrar no ADR.
- A persistência é feita no **PostgreSQL** (usuários, resultados, histórico e vetores) e no **OCI Object Storage** (originais, JSONs e backups), conforme ADR-0013 e ADR-0014. O índice vetorial é reconstruível a partir dos originais no bucket.
- Prazo: primeira entrega em **24/11/2026**, com seleção, seguida de uma fase final (data a confirmar com os organizadores). A partir de 18/10 restam 37 dias.
- A conta Always Free da OCI e a região principal ainda precisam ser criadas (ver [06 - Backlogs](./06%20-%20Backlogs.md#5-riscos-que-afetam-o-backlog)).

## 5. Fora de escopo (v2)

Recuperação de senha, OAuth, ranking entre usuários, multimodal, onboarding por estilos de aprendizagem, repetição espaçada (SM-2), Feynman reverso e busca na web (esta última adiada, ver RN-13).
