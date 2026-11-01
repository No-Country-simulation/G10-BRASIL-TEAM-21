# 07 - Convenções

> **Versão:** v2 · **Data:** 2026-10-17
> Objetivo: reduzir atrito entre front e back, manter o repositório limpo e evitar retrabalho até a entrega de 24/11/2026. Em caso de dúvida, vale o que estiver aqui; para mudar, abra um PR neste arquivo.

---

## 1. Idioma

| Item | Idioma |
|---|---|
| Interface, mensagens de erro e documentação | PT-BR |
| Campos de API, entidades e valores de enumerações | PT-BR **sem acentos** (alinhado ao edital) |
| Nomes de classes, funções e variáveis de infraestrutura | Inglês ou português, **de forma consistente dentro do módulo**. Regras de domínio usam o vocabulário do domínio (`xp`, `nivel`, `adaptacao`) |
| Commits e PRs | PT-BR |

## 2. Python (back-end)

- **Versão:** Python 3.11 ou superior.
- **Estilo e lint:** `ruff` (lint e formatação). PEP 8. Linhas de até 100 caracteres.
- **Tipagem:** *type hints* em funções públicas. `mypy` opcional.
- **Pydantic:** todo dado que cruza uma fronteira (API, LLM, storage) tem schema. Saída do LLM **sempre** validada.
- **Regras de domínio puras:** `domain/` não faz I/O (sem rede, disco, banco ou LLM), para ser testável sem mocks.
- **Dependências entre camadas:** `api` → `services`/`agents`/`rag` → `ports` ← `infra`. `infra` (SQLAlchemy, OCI, provedores de LLM) nunca é importado pelo domínio.
- **Banco:** SQLAlchemy 2.x. Toda consulta de recurso do usuário filtra por `usuario_id` do token **na própria consulta**. Transações curtas; o resultado de uma adaptação, o XP e o perfil são gravados na mesma transação.
- **Migrações:** Alembic. Toda mudança de esquema vem com migração **no mesmo PR**. Migração já aplicada na `main` **não é editada**: cria-se outra.
- **Configuração:** `pydantic-settings` lendo variáveis de ambiente. Nada de valores fixos de segredo no código.
- **Erros:** exceções de domínio tipadas, convertidas em respostas padronizadas por um *handler* central. Nada de `except:` genérico que engole o erro.
- **Logs:** estruturados (JSON) com `request_id`. Nunca registrar senha, token, e-mail completo ou conteúdo integral de documento.
- **Dependências:** fixadas em `pyproject.toml` com versões; novas dependências são justificadas no PR.

## 3. Front-end

- Tipos gerados a partir do `openapi.json`. Não duplicar tipos à mão.
- Todo consumo de API trata `null` nos campos opcionais e os códigos de erro do contrato.
- `armazenamento_oci.status_upload = "falha"` ou `"pendente"` é **aviso**, não erro: o resultado existe e pode ser reaberto.
- Textos de interface centralizados (facilita revisão do PT-BR).
- Estados explícitos: carregando, vazio, erro e sucesso.
- Token armazenado de forma consciente do risco (ver [04 - Arquitetura](./04%20-%20Arquitetura.md)); nunca registrado em console ou logs.
- Framework: React com Vite ([ADR-0012](./adr/ADR-0012-framework-do-front-end.md)). Convenções específicas (estrutura de pastas, estado, rotas) entram aqui quando o projeto for criado.

### 3.1 Organização e consumo da API (T5 / US-003)

- React + Vite com TypeScript em modo estrito. Preservar os diretórios `src/componentes/`, `src/paginas/` e `src/hooks/` introduzidos na T4; não criar diretórios paralelos `components/` ou `pages/`.
- `src/api/schema.d.ts` é gerado de `backend/docs/openapi.json` por `npm run gerar:tipos`. Aliases podem referenciar esses modelos; não copiar interfaces de domínio manualmente.
- `src/api/` concentra configuração, HTTP, erros e funções de adaptação. Páginas não usam `fetch` diretamente. `VITE_USE_MOCK=true` seleciona fixtures; qualquer outro valor seleciona HTTP em `VITE_API_URL` (base com `/api/v1`). Não trocar erro HTTP por sucesso mock automaticamente.
- `frontend/mocks/` contém as fixtures canônicas. `npm run mocks:sync` copia os JSONs para `src/mocks/` antes de desenvolvimento, testes e build. Editar a origem; manter a cópia sincronizada.
- `src/texts/pt-BR.ts` centraliza textos de interface e mensagens dos códigos da seção 8 do contrato. Conteúdo educacional recebido da API fica nos dados, sem tradução ou reescrita pelo front.
- React Router preserva `/login`, `/cadastro`, `/upload`, `/resultado/:id`, `/historico` e `/perfil`. `recente` é uma rota local para o resultado recém-gerado, mantido apenas em memória; não é um identificador retornado pela API.
- Estados da prova de conceito derivam da requisição assíncrona, com cancelamento e nova tentativa. Parâmetros de demonstração e controles de cenários só são aplicados com mock ativo.
- O cliente aceita um provedor de Bearer token em memória (`src/api/sessao.ts`); não persiste tokens e não faz logs de credenciais. Integração das páginas de autenticação pertence ao fluxo de acesso.
- Executar `npm run typecheck`, `npm run lint`, `npm test` e `npm run build`. Fixtures são verificadas contra o JSON Schema do OpenAPI e contra o exemplo completo de Flashcards em docs/05.
- O ADR-0012 e docs/09 são referenciados pelo planejamento, mas não estão presentes nesta revisão do repositório. Este registro documenta a implementação existente; não presume o conteúdo ou a aprovação dos documentos ausentes.

## 4. API

- Rotas em português, minúsculas, no plural, com hífen: `/testes-nivel`, `/adaptacoes`.
- Verbos HTTP corretos. Códigos de status conforme [05 - Contrato de API](./05%20-%20Contrato%20de%20API.md).
- Mudanças aditivas no contrato são livres; mudanças que quebram exigem novo `versao_schema`, ADR (se for decisão relevante) e aviso à equipe.
- Antes de mudar um schema, **avise o front** e atualize o OpenAPI no mesmo PR.

## 5. Git

### 5.1 Branches fixas

| Branch | Papel | Recebe de | Proteção |
|---|---|---|---|
| `main` | Estado entregável e demonstrável. Só recebe o que passou na homologação. | `homolog` | Protegida, somente por PR |
| `homolog` | Portão de validação antes da `main`. Persistente. | `dev` | Protegida, somente por PR |
| `dev` | Integração do dia a dia. Todo trabalho entra aqui primeiro. | branches de trabalho | Protegida, somente por PR |

Não há branches de longa duração por área (`frontend`, `backend`, `ai-agent`). A área é identificada pelo **nome da branch de trabalho**, pelo **escopo do commit** e pelo **`CODEOWNERS`**. Motivo: uma mudança de contrato mexe em front e back no mesmo PR, e branches por área adiam a integração, multiplicam merges por feature e geram mais de um *head* de migração Alembic.

### 5.2 Branches de trabalho

Formato: `<tipo>/<area>-<assunto>`, em minúsculas, com hífens. Sempre saem de `dev` e voltam para `dev`.

| Área | Pasta | Exemplos |
|---|---|---|
| `back` | `backend/` (API, serviços, banco, RAG, armazenamento) | `feat/back-upload-documento`, `fix/back-expiracao-token` |
| `front` | `frontend/` | `feat/front-tela-login` |
| `agent` | `backend/app/agents/` (grafo, nós, prompts) | `feat/agent-no-verificar-fidelidade` |
| `docs` | `docs/` | `docs/adr-0011-llm` |
| `infra` | Docker, compose, CI, configuração | `chore/infra-dockerfile-front` |

- Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- Mudança que cruza áreas (ex.: contrato) é **um PR só**, com a área principal no nome e os `CODEOWNERS` das pastas tocadas revisando.
- Vida curta: no máximo 2 a 3 dias. Divida histórias grandes.
- `hotfix/<assunto>` sai de `main` e só é usado para correção urgente da versão demonstrável; depois do merge em `main`, a correção volta para `homolog` e `dev`.

### 5.3 Fluxo e tipo de merge

```text
feat/back-xxx  ─┐
feat/front-xxx ─┼─► dev ──► homolog ──► main
feat/agent-xxx ─┘   (squash)  (merge commit)  (merge commit)
```

- **Branch de trabalho para `dev`:** *squash merge*, ao menos 1 aprovação.
- **`dev` para `homolog` e `homolog` para `main`:** *merge commit*, **nunca squash**. Squash em promoção faz as branches divergirem e gera conflito falso na promoção seguinte.
- Apague a branch de trabalho após o merge. Nunca faça *push* direto em `main`, `homolog` ou `dev`.
- **Critério de homologação:** clone limpo, `cp .env.example .env`, `docker compose up --build` e o fumaça dos 3 cenários de demonstração (doc 04, seção de testes) sem erro. O que falhar volta como `fix/...` para `dev`.

### 5.4 Marcos (tags)

Tags anotadas na `main`: `gate-1` (7/11), `gate-2` (20/11, congelamento) e `entrega-1` (24/11). Marcos intermediários, se houver, seguem `v0.X.0`.

### 5.5 Commits (Conventional Commits em PT-BR)

```text
<tipo>(<escopo>): <resumo no imperativo, até 72 caracteres>

feat(rag): adiciona chunking deterministico
fix(auth): corrige expiracao do token
docs(adr): registra decisao sobre analogias
test(xp): cobre teto diario de geracao
chore(ci): adiciona lint no pipeline
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`. Escopos sugeridos: `rag`, `agents`, `api`, `auth`, `xp`, `storage`, `db`, `front`, `docs`, `ci`, `infra`.

Commits claros e colaborativos fazem parte da avaliação: **todos do time commitam**.

### 5.6 Pull requests

- Título no mesmo padrão dos commits (vira a mensagem do squash).
- Base correta: `dev` para trabalho; `homolog` só a partir de `dev`; `main` só a partir de `homolog`.
- Pequeno, com o que muda, a história relacionada e como testar. Checklist da seção 9.
- Ao menos 1 aprovação; autor não aprova o próprio PR.

### 5.7 Configuração do repositório no GitHub

- Branch protection (ou *ruleset*) em `main`, `homolog` e `dev`: exigir PR, exigir 1 aprovação, exigir resolução de conversas, bloquear *force push* e exclusão.
- Exigir *status checks* **somente depois** que o CI existir; o CI é responsabilidade de quem cuida de DevOps no time e deve ser desenhado a partir deste fluxo (nome de branch, título de PR, lint, testes, `docker compose config`). Evite filtro `paths:` em workflow com check obrigatório: o check não roda e o PR trava.
- Merge: habilitar *squash* e *merge commit*; desabilitar *rebase*. Apagar branch automaticamente após o merge.
- `CODEOWNERS` por pasta (`backend/`, `frontend/`, `backend/app/agents/`, `docs/`) e exigir revisão de code owner em `main` e `homolog`.

## 6. Segredos e Always Free

- `.env` e chaves da OCI (`*.pem`) **no `.gitignore`** desde o primeiro commit.
- `.env.example` com nomes de variáveis e nenhum valor real. Isso inclui a senha do banco: nunca versionar as credenciais, nem as de desenvolvimento.
- Se um segredo for versionado por engano: **revogar e gerar outro** imediatamente (apagar do histórico não basta).
- Só serviços Always Free da OCI. Qualquer novo recurso na OCI precisa de confirmação de que é Always Free **antes** de ser criado.
- O PostgreSQL roda em container e não é um serviço da OCI. Não criar banco gerenciado pago.
- Chaves de LLM com limites de uso configurados quando o provedor permitir.

## 7. Testes

Princípio: testar o que **quebra de verdade**, sem perseguir cobertura.

- **Obrigatório:** regras puras (XP, níveis, teto diário, domínio de conceitos), contrato da API (autenticação, validação, erros), chunking determinístico e o que só o banco garante (e-mail único, XP uma vez por pergunta, transação do resultado com o XP).
- **Sem rede nos testes de unidade e de contrato:** usar `LocalFileStorage`, repositórios em memória e LLM falso.
- **Testes de integração do banco** rodam contra o PostgreSQL do Compose (com `pgvector`), nunca contra SQLite, para não esconder diferenças de dialeto.
- **Não testar com teste unitário** a qualidade textual do LLM. Para isso, usar os cenários de demo como conferência manual registrada.
- Um teste que passa mesmo com a funcionalidade quebrada deve ser removido ou corrigido.

## 8. Documentação

- Tudo em `docs/`, em Markdown, com os arquivos numerados `01` a `08`.
- **ADR** (`docs/adr/`) para decisões de arquitetura ou produto difíceis de reverter, com contexto, decisão, alternativas e consequências. Numeração sequencial `ADR-NNNN`. Um ADR aceito não é editado: é **substituído** por outro (só o campo de status do antigo muda).
- **PRD** (`docs/prd/`) para cada funcionalidade relevante, com problema, objetivos, requisitos, regras e critérios de aceite.
- Mudou regra de negócio, contrato ou arquitetura? **Atualize o documento no mesmo PR.**
- Os títulos dos documentos são **âncoras de link** usadas por ADRs e PRDs. Ao renomear um título, procure e corrija os links que apontam para ele.
- O README da raiz resume e aponta para `docs/`.

## 9. Revisão de PR (checklist)

- [ ] Critérios de aceite da história atendidos
- [ ] Sem segredos, sem dados pessoais em logs
- [ ] Erros tratados com mensagem amigável
- [ ] Schemas e OpenAPI atualizados
- [ ] Migração Alembic incluída, se o esquema mudou
- [ ] Consultas de recursos do usuário filtradas por `usuario_id`
- [ ] Testes relevantes incluídos
- [ ] Documentação atualizada
- [ ] Nenhum recurso fora da camada Always Free
