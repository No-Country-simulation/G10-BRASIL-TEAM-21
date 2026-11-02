# Frontend Â· React + Vite + TypeScript

T5 / US-003: cliente de API com alternÃ¢ncia entre fixtures do contrato e backend real.
T6: tipos gerados do OpenAPI com verificaÃ§Ã£o de sincronizaÃ§Ã£o no CI.
Preserva o roteamento e os diretÃ³rios da T4. Regras em
[docs/07 Â§3](../docs/07%20-%20Conven%C3%A7%C3%B5es.md#3-front-end); dados e erros em
[docs/05](../docs/05%20-%20Contrato%20de%20API.md).

## Executar sem backend

Use Node 22 atualizado (mesma linha do CI) ou Node 26 (Dockerfile).
O projeto jÃ¡ existe; nÃ£o execute `npm create vite` novamente.

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Abra `http://localhost:5173/resultado/demo-1`. A fixture Ã© carregada assincronamente;
os controles da demonstraÃ§Ã£o permitem alternar cenÃ¡rios. TambÃ©m Ã© possÃ­vel abrir
`/upload` e usar o link para o exemplo, ou preencher tÃ­tulo/texto e gerar a demonstraÃ§Ã£o.
No mock, o conteÃºdo e os parÃ¢metros efetivos sÃ£o os do exemplo fixo do contrato;
nÃ£o hÃ¡ processamento do texto digitado. O seletor de arquivo e outros formatos ficam
indisponÃ­veis nesse modo para nÃ£o sugerir uma geraÃ§Ã£o que ainda nÃ£o existe.

## ConfiguraÃ§Ã£o e modo real

| VariÃ¡vel | Valor e comportamento |
|---|---|
| `VITE_USE_MOCK` | Somente a string `true` habilita mocks. Ausente, `false` ou outro valor usa HTTP. |
| `VITE_API_URL` | Base pÃºblica da API, incluindo `/api/v1`. PadrÃ£o `/api/v1`; o exemplo local usa `http://localhost:8000/api/v1`. |

Para chamar o backend, altere `VITE_USE_MOCK=false` no `.env` e reinicie o Vite.
As variÃ¡veis `VITE_*` sÃ£o pÃºblicas e incorporadas ao build; nunca coloque segredos nelas.
O cliente nÃ£o substitui erros reais por mocks. Os controles/query strings de simulaÃ§Ã£o
nÃ£o alteram as respostas HTTP.

O mÃ³dulo `src/api/sessao.ts` fornece `definirTokenAcesso(token)` e
`definirTokenAcesso(null)` ao futuro fluxo de autenticaÃ§Ã£o. O cliente obtÃ©m o token
em memÃ³ria a cada requisiÃ§Ã£o e acrescenta `Authorization: Bearer ...`; nÃ£o usa
`localStorage` nem registra tokens. Recarregar a pÃ¡gina elimina a sessÃ£o volÃ¡til.
Para testes isolados, `criarApiAdaptacoes(config, obterToken, transporte)` permite
injetar token e transporte sem fazer rede.

As pÃ¡ginas de login/cadastro, histÃ³rico e perfil continuam prÃ©vias da T4, com textos
centralizados e indicaÃ§Ã£o de demonstraÃ§Ã£o. A T5 nÃ£o implementa autenticaÃ§Ã£o completa,
listagem real do histÃ³rico, XP ou Teste de NÃ­vel. RequisiÃ§Ãµes reais sem sessÃ£o podem
retornar 401. Na revisÃ£o atual, as rotas contratuais de adaptaÃ§Ãµes, perfil e
`POST /documentos` ainda retornam 501 apÃ³s autenticaÃ§Ã£o: isso deve aparecer como erro
amigÃ¡vel, nÃ£o como conteÃºdo gerado. O upload implementado separadamente em
`/documentos/upload` nÃ£o substitui silenciosamente o endpoint do contrato.

O Compose recebe `VITE_USE_MOCK` da configuraÃ§Ã£o da raiz. O README acima descreve a
execuÃ§Ã£o direta do Vite; a publicaÃ§Ã£o dos assets pelo nginx da stack permanece sob
responsabilidade da configuraÃ§Ã£o de infraestrutura existente.

## Estrutura e rotas

```text
frontend/
  mocks/adaptacao-flashcards.json     # origem: exemplo completo de docs/05 Â§5.2
  scripts/sincronizar-mocks.mjs       # copia fixtures para src/
  src/
    api/                            # configuraÃ§Ã£o, HTTP, sessÃ£o, erros e adaptaÃ§Ãµes
      api-types.ts                   # gerado e versionado, nÃ£o editar manualmente
    components/                    # Layout, EstadoTela, PacoteAdaptacao
    pages/                        # pÃ¡ginas da T4
    hooks/                          # estados de demonstraÃ§Ã£o das prÃ©vias
    mocks/                          # cÃ³pia sincronizada, nÃ£o editar manualmente
    texts/pt-BR.ts                   # todos os rÃ³tulos e mensagens de interface
  tests/                            # cliente, contrato e fluxo de resultado
```

React Router mantÃ©m `/login`, `/cadastro`, `/upload`, `/resultado/:id`, `/historico`
e `/perfil`. `/resultado/recente` usa o Ãºltimo resultado gerado em memÃ³ria: nÃ£o Ã© um
ID recebido do contrato. No modo real, apÃ³s recarregar essa rota, Ã© necessÃ¡rio gerar
novamente ou abrir `/resultado/<id-real>`. A resposta de geraÃ§Ã£o nÃ£o fornece um
`adaptacao_id`; a T5 nÃ£o acrescenta esse campo ao contrato.

## CenÃ¡rios reproduzÃ­veis

Com mock ativo, abra `/resultado/demo-1` com uma das query strings:

| CenÃ¡rio | Query string |
|---|---|
| Exemplo completo de Flashcards | `?cenario=completo` |
| Analogias, microlearning, evoluÃ§Ã£o e nÃ­vel do documento nulos | `?cenario=nulos` |
| Lista de itens vazia | `?cenario=vazio` |
| Carregamento contÃ­nuo, cancelÃ¡vel ao navegar | `?cenario=carregando` |
| Erro padronizado com referÃªncia de suporte | `?cenario=erro&codigo=BANCO_INDISPONIVEL` |
| SessÃ£o expirada | `?cenario=erro&codigo=TOKEN_EXPIRADO` |
| Aviso de upload pendente | `?cenario=pendente` |
| Aviso de falha no upload | `?cenario=falha` |

`?estado=carregando|vazio|erro` permanece disponÃ­vel nas prÃ©vias da T4 e como alias
no resultado. Erros conhecidos possuem mensagens PT-BR centralizadas; cÃ³digos novos,
HTML inesperado e falhas de conexÃ£o recebem mensagens de fallback. O alias temporÃ¡rio
`EMAIL_EXISTE` do cadastro atual Ã© apresentado como `EMAIL_JA_CADASTRADO`.
Detalhes de validaÃ§Ã£o sÃ£o associados aos campos, sem exibir mensagens tÃ©cnicas.

O resultado renderiza Flashcards, metadados, qualidade, fontes, analogias com limite,
blocos de estudo e evoluÃ§Ã£o quando presentes. Opcionais `null`/ausentes nÃ£o derrubam
a pÃ¡gina. Upload pendente/falho continua sendo aviso; o conteÃºdo permanece acessÃ­vel.
O renderizador preserva suporte aos tipos de itens dos outros quatro formatos, mas a
fixture/prova de conceito da T5 Ã© exclusivamente Flashcards.

## Contrato e validaÃ§Ã£o

```bash
npm run gen:api
npm run check:api
npm run mocks:sync
npm run typecheck
npm run lint
npm test
npm run build
```

`gen:api` lÃª `backend/docs/openapi.json`; `gerar:tipos` continua disponÃ­vel como alias.
Tipos de domÃ­nio sÃ£o aliases dos modelos gerados; interfaces locais descrevem apenas
configuraÃ§Ã£o e estado da interface.
`strict` estÃ¡ habilitado no TypeScript para conferir os casos `null`.

Edite apenas `mocks/adaptacao-flashcards.json`. A sincronizaÃ§Ã£o acontece antes de
`dev`, `test` e `build`; ambas as cÃ³pias sÃ£o versionadas. Testes verificam igualdade
com o exemplo de docs/05 (normalizando apenas os espaÃ§os de indentaÃ§Ã£o), conformidade
com o JSON Schema do OpenAPI e os cenÃ¡rios derivados.

DependÃªncias de desenvolvimento da T5: Vitest executa os testes; Testing Library e
jsdom verificam estados e navegaÃ§Ã£o; AJV e ajv-formats validam fixtures contra o
OpenAPI. Os testes nÃ£o fazem rede e nÃ£o exigem banco, LLM ou OCI. O CI existente
executa `typecheck`, `test`, lint e build pelos scripts do projeto.

## Tipos OpenAPI Â· T6

O `openapi-typescript` Ã© uma dependÃªncia de desenvolvimento versionada no lockfile.
`npm ci` instala o gerador local; nÃ£o Ã© necessÃ¡ria uma instalaÃ§Ã£o global. A fonte da
verdade sÃ£o os schemas Pydantic, publicados em `backend/docs/openapi.json`. A geraÃ§Ã£o
padrÃ£o usa esse arquivo, sem precisar iniciar a API ou acessar banco, LLM e OCI.
O FastAPI tambÃ©m serve o documento em `http://localhost:8000/openapi.json` (fora de
`/api/v1`); esse endpoint pode ser usado para consultar o contrato em execuÃ§Ã£o.

```text
backend/app/schemas/ + rotas FastAPI
              â†“ exportaÃ§Ã£o do backend
backend/docs/openapi.json
              â†“ npm run gen:api
frontend/src/api/api-types.ts
              â†“ aliases em api/tipos.ts
cliente HTTP, mocks e componentes
```

`api-types.ts` deve ser commitado. NÃ£o formate nem edite esse arquivo Ã  mÃ£o.
`tipos.ts` apenas referencia `components['schemas']` do arquivo gerado para modelos
como `Adaptacao`, `AdaptacaoRequest`, `Documento`, `ErroResposta` e `ItemConteudo`.
Interfaces de configuraÃ§Ã£o, estado, cenÃ¡rios de mock e props sÃ£o tipos locais de
interface, nÃ£o duplicaÃ§Ãµes das respostas do backend. A importaÃ§Ã£o do JSON do mock
usa uma asserÃ§Ã£o de tipo porque seus valores string nÃ£o sÃ£o inferidos como enums;
as fixtures e variantes sÃ£o validadas contra o JSON Schema publicado nos testes.

Ao mudar schemas ou rotas, inclua no **mesmo PR**:

1. A alteraÃ§Ã£o no backend e a atualizaÃ§Ã£o da documentaÃ§Ã£o afetada.
2. O OpenAPI atualizado, exportado na pasta `backend/` com
   `python -m scripts.export_openapi`, no ambiente de desenvolvimento do backend.
3. Os tipos regenerados na pasta `frontend/` com `npm run gen:api`.
4. Os ajustes de consumidores e mocks exigidos pelo novo contrato.
5. A validaÃ§Ã£o com `npm run check:api`, `npm run typecheck`, `npm run lint`,
   `npm test` e `npm run build`.

`check:api` gera uma cÃ³pia em diretÃ³rio temporÃ¡rio, compara com o arquivo versionado
e remove os temporÃ¡rios. NÃ£o modifica o contrato ou os tipos do projeto. Se o arquivo
estiver ausente, editado Ã  mÃ£o ou desatualizado, termina com cÃ³digo 1 e orienta a
regeneraÃ§Ã£o. Os parÃ¢metros locais `--source` e `--output` do script permitem verificar
cÃ³pias isoladas:

```bash
npm run check:api -- --source /caminho/openapi.json --output /caminho/api-types.ts
```

Sem parÃ¢metros, os caminhos sÃ£o relativos ao prÃ³prio script,
independentemente da pasta de onde ele foi chamado.

O CI executa `check:api` explicitamente antes do lint/typecheck/testes/build do front.
A detecÃ§Ã£o de mudanÃ§as tambÃ©m inclui o OpenAPI, schemas, routers, criaÃ§Ã£o do app,
script de exportaÃ§Ã£o e docs/05 do backend. O teste existente do backend confere a
sincronizaÃ§Ã£o entre FastAPI e o OpenAPI versionado; o novo check confere OpenAPI e
TypeScript. O CI verifica os arquivos e nÃ£o cria commits automaticamente.

Os testes da T6 alteram apenas cÃ³pias temporÃ¡rias: comprovam falha apÃ³s mudanÃ§a de
contrato ou ediÃ§Ã£o manual dos tipos, falha com tipos ausentes/documento invÃ¡lido e
sucesso apÃ³s regeneraÃ§Ã£o. O arquivo real do projeto Ã© preservado.

## ReferÃªncias pendentes

O planejamento cita `docs/09` e o ADR-0012, mas esses arquivos nÃ£o estÃ£o presentes
na revisÃ£o usada pela T5. Foram seguidos o contrato publicado, os schemas, as
convenÃ§Ãµes de docs/07 e a estrutura React/Vite/TypeScript jÃ¡ adotada. NÃ£o foi criado
um ADR retroativo nem presumida aprovaÃ§Ã£o de decisÃµes ausentes.

