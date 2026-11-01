# Frontend · React + Vite + TypeScript

T5 / US-003: cliente de API com alternância entre fixtures do contrato e backend real.
Preserva o roteamento e os diretórios da T4. Regras em
[docs/07 §3](../docs/07%20-%20Conven%C3%A7%C3%B5es.md#3-front-end); dados e erros em
[docs/05](../docs/05%20-%20Contrato%20de%20API.md).

## Executar sem backend

Use Node 22 atualizado (mesma linha do CI) ou Node 26 (Dockerfile).
O projeto já existe; não execute `npm create vite` novamente.

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Abra `http://localhost:5173/resultado/demo-1`. A fixture é carregada assincronamente;
os controles da demonstração permitem alternar cenários. Também é possível abrir
`/upload` e usar o link para o exemplo, ou preencher título/texto e gerar a demonstração.
No mock, o conteúdo e os parâmetros efetivos são os do exemplo fixo do contrato;
não há processamento do texto digitado. O seletor de arquivo e outros formatos ficam
indisponíveis nesse modo para não sugerir uma geração que ainda não existe.

## Configuração e modo real

| Variável | Valor e comportamento |
|---|---|
| `VITE_USE_MOCK` | Somente a string `true` habilita mocks. Ausente, `false` ou outro valor usa HTTP. |
| `VITE_API_URL` | Base pública da API, incluindo `/api/v1`. Padrão `/api/v1`; o exemplo local usa `http://localhost:8000/api/v1`. |

Para chamar o backend, altere `VITE_USE_MOCK=false` no `.env` e reinicie o Vite.
As variáveis `VITE_*` são públicas e incorporadas ao build; nunca coloque segredos nelas.
O cliente não substitui erros reais por mocks. Os controles/query strings de simulação
não alteram as respostas HTTP.

O módulo `src/api/sessao.ts` fornece `definirTokenAcesso(token)` e
`definirTokenAcesso(null)` ao futuro fluxo de autenticação. O cliente obtém o token
em memória a cada requisição e acrescenta `Authorization: Bearer ...`; não usa
`localStorage` nem registra tokens. Recarregar a página elimina a sessão volátil.
Para testes isolados, `criarApiAdaptacoes(config, obterToken, transporte)` permite
injetar token e transporte sem fazer rede.

As páginas de login/cadastro, histórico e perfil continuam prévias da T4, com textos
centralizados e indicação de demonstração. A T5 não implementa autenticação completa,
listagem real do histórico, XP ou Teste de Nível. Requisições reais sem sessão podem
retornar 401. Na revisão atual, as rotas contratuais de adaptações, perfil e
`POST /documentos` ainda retornam 501 após autenticação: isso deve aparecer como erro
amigável, não como conteúdo gerado. O upload implementado separadamente em
`/documentos/upload` não substitui silenciosamente o endpoint do contrato.

O Compose recebe `VITE_USE_MOCK` da configuração da raiz. O README acima descreve a
execução direta do Vite; a publicação dos assets pelo nginx da stack permanece sob
responsabilidade da configuração de infraestrutura existente.

## Estrutura e rotas

```text
frontend/
  mocks/adaptacao-flashcards.json     # origem: exemplo completo de docs/05 §5.2
  scripts/sincronizar-mocks.mjs       # copia fixtures para src/
  src/
    api/                            # configuração, HTTP, sessão, erros e adaptações
      schema.d.ts                   # gerado do OpenAPI, não editar manualmente
    componentes/                    # Layout, EstadoTela, PacoteAdaptacao
    paginas/                        # páginas da T4
    hooks/                          # estados de demonstração das prévias
    mocks/                          # cópia sincronizada, não editar manualmente
    texts/pt-BR.ts                   # todos os rótulos e mensagens de interface
  tests/                            # cliente, contrato e fluxo de resultado
```

React Router mantém `/login`, `/cadastro`, `/upload`, `/resultado/:id`, `/historico`
e `/perfil`. `/resultado/recente` usa o último resultado gerado em memória: não é um
ID recebido do contrato. No modo real, após recarregar essa rota, é necessário gerar
novamente ou abrir `/resultado/<id-real>`. A resposta de geração não fornece um
`adaptacao_id`; a T5 não acrescenta esse campo ao contrato.

## Cenários reproduzíveis

Com mock ativo, abra `/resultado/demo-1` com uma das query strings:

| Cenário | Query string |
|---|---|
| Exemplo completo de Flashcards | `?cenario=completo` |
| Analogias, microlearning, evolução e nível do documento nulos | `?cenario=nulos` |
| Lista de itens vazia | `?cenario=vazio` |
| Carregamento contínuo, cancelável ao navegar | `?cenario=carregando` |
| Erro padronizado com referência de suporte | `?cenario=erro&codigo=BANCO_INDISPONIVEL` |
| Sessão expirada | `?cenario=erro&codigo=TOKEN_EXPIRADO` |
| Aviso de upload pendente | `?cenario=pendente` |
| Aviso de falha no upload | `?cenario=falha` |

`?estado=carregando|vazio|erro` permanece disponível nas prévias da T4 e como alias
no resultado. Erros conhecidos possuem mensagens PT-BR centralizadas; códigos novos,
HTML inesperado e falhas de conexão recebem mensagens de fallback. O alias temporário
`EMAIL_EXISTE` do cadastro atual é apresentado como `EMAIL_JA_CADASTRADO`.
Detalhes de validação são associados aos campos, sem exibir mensagens técnicas.

O resultado renderiza Flashcards, metadados, qualidade, fontes, analogias com limite,
blocos de estudo e evolução quando presentes. Opcionais `null`/ausentes não derrubam
a página. Upload pendente/falho continua sendo aviso; o conteúdo permanece acessível.
O renderizador preserva suporte aos tipos de itens dos outros quatro formatos, mas a
fixture/prova de conceito da T5 é exclusivamente Flashcards.

## Contrato e validação

```bash
npm run gerar:tipos
npm run mocks:sync
npm run typecheck
npm run lint
npm test
npm run build
```

`gerar:tipos` lê `backend/docs/openapi.json`. Tipos de domínio são aliases dos modelos
gerados; interfaces locais descrevem apenas configuração e estado da interface.
`strict` está habilitado no TypeScript para conferir os casos `null`.

Edite apenas `mocks/adaptacao-flashcards.json`. A sincronização acontece antes de
`dev`, `test` e `build`; ambas as cópias são versionadas. Testes verificam igualdade
com o exemplo de docs/05 (normalizando apenas os espaços de indentação), conformidade
com o JSON Schema do OpenAPI e os cenários derivados.

Dependências de desenvolvimento da T5: Vitest executa os testes; Testing Library e
jsdom verificam estados e navegação; AJV e ajv-formats validam fixtures contra o
OpenAPI. Os testes não fazem rede e não exigem banco, LLM ou OCI. O CI existente
executa `typecheck`, `test`, lint e build pelos scripts do projeto.

## Referências pendentes

O planejamento cita `docs/09` e o ADR-0012, mas esses arquivos não estão presentes
na revisão usada pela T5. Foram seguidos o contrato publicado, os schemas, as
convenções de docs/07 e a estrutura React/Vite/TypeScript já adotada. Não foi criado
um ADR retroativo nem presumida aprovação de decisões ausentes.
