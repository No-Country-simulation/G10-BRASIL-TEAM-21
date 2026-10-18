# 05 - Contrato de API

> **Versão do contrato:** `1.0` (ainda não publicado; as alterações de 17/10/2026 estão em "Mudanças em relação ao rascunho de 13/10") · **Data:** 2026-10-17
> **Fonte da verdade:** os schemas Pydantic em `backend/app/schemas/`. O FastAPI publica o OpenAPI em `/openapi.json` e a documentação interativa em `/docs`. O front-end deve **gerar seus tipos a partir do OpenAPI** e trabalhar com mocks até o back-end ficar pronto.
> **Relacionados:** [02 - Requisitos](./02%20-%20Requisitos.md) · [03 - Modelo de Domínio](./03%20-%20Modelo%20de%20Dom%C3%ADnio.md) · [ADR-0009](./adr/ADR-0009-contrato-json-estendido-compativel-com-edital.md)

---

## Mudanças em relação ao rascunho de 13/10

Como o contrato ainda não foi publicado nem consumido, estas correções entram na versão `1.0` sem aumentar `versao_schema`.

1. **`analogias` e `microlearning` passam a ser campos de topo da resposta**, ao lado de `conteudo_adaptado`, e não filhos dele. O rascunho anterior os aninhava no exemplo, mas o modelo de domínio e o ADR-0009 os tratam como extensões de topo; manter os dois lugares quebraria a geração de tipos do front.
2. **`nivel_documento_estimado` é estimado na ingestão** (RN-18) e já vem no `POST /documentos`. Pode ser `null` se o LLM estiver indisponível nesse momento.
3. **`status_upload`** passa a existir também na resposta de `POST /documentos`, com os valores `pendente`, `concluido` e `falha` (RN-17). Falha no bucket **não derruba** a requisição.
4. **Novo erro `BANCO_INDISPONIVEL`** (503). `ARMAZENAMENTO_INDISPONIVEL` fica restrito a operações que dependem do bucket.
5. **`GET /health`** passa a verificar o banco e a extensão `pgvector`, além do bucket.

---

## 1. Convenções

| Tema | Regra |
|---|---|
| Base | `/api/v1` |
| Formato | JSON em UTF-8. Upload de arquivo em `multipart/form-data` |
| Campos | `snake_case`, em português sem acentos (alinhado ao edital) |
| Valores de enumerações | Sem acentos (ver [03 - Modelo de Domínio](./03%20-%20Modelo%20de%20Dom%C3%ADnio.md#3-enumera%C3%A7%C3%B5es)) |
| Identificadores | Strings opacas. O front não deve interpretá-los. Os exemplos usam prefixos curtos por legibilidade |
| Datas | ISO 8601 com fuso |
| Autenticação | `Authorization: Bearer <token>` em todos os endpoints, exceto `/auth/cadastro`, `/auth/login` e `/health` |
| Idempotência | Não há em v1. Cada `POST /adaptacoes` gera uma nova adaptação |
| Evolução do contrato | **Mudanças aditivas** são livres. Mudança que quebra exige novo `versao_schema` e aviso à equipe |
| Campos opcionais | Campos de funcionalidades ainda não entregues (`analogias`, `microlearning`, `trilha_evolucao`) retornam `null`. O front **deve tolerar `null`** |
| Leitura | Listagens e reabertura de adaptações são lidas do **banco**, nunca do bucket (ADR-0013) |

## 2. Endpoints

| Método | Rota | Descrição | Auth | RF |
|---|---|---|---|---|
| POST | `/auth/cadastro` | Cria usuário | Não | RF-01 |
| POST | `/auth/login` | Retorna token de acesso | Não | RF-02 |
| POST | `/auth/logout` | Encerra a sessão (o cliente descarta o token) | Sim | RF-03 |
| GET | `/usuarios/me` | Dados básicos do usuário logado | Sim | RF-01 |
| POST | `/documentos` | Envia e indexa um documento | Sim | RF-04, RF-05 |
| GET | `/documentos` | Lista documentos do usuário | Sim | RF-12 |
| GET | `/documentos/{documento_id}` | Detalha um documento | Sim | RF-12 |
| POST | `/adaptacoes` | Gera o pacote educacional | Sim | RF-06 a RF-11 |
| GET | `/adaptacoes` | Lista adaptações do usuário (resumo) | Sim | RF-12 |
| GET | `/adaptacoes/{adaptacao_id}` | Reabre uma adaptação (JSON completo) | Sim | RF-12 |
| POST | `/adaptacoes/{adaptacao_id}/respostas` | Responde o quiz, valida e concede XP | Sim | RF-13 |
| GET | `/perfil` | Trilha de evolução do usuário | Sim | RF-14 |
| POST | `/testes-nivel` | Inicia o Teste de Nível | Sim | RF-16 |
| POST | `/testes-nivel/{teste_id}/respostas` | Envia respostas e calcula o resultado | Sim | RF-16 |
| GET | `/health` | Saúde da API, do banco, do `pgvector` e do bucket | Não | RNF-09 |

## 3. Autenticação

**`POST /auth/cadastro`**

```json
{
  "nome": "Ana Souza",
  "email": "ana@exemplo.com",
  "senha": "********",
  "nivel_declarado": "Iniciante"
}
```

Resposta `201`:

```json
{
  "usuario_id": "usr-7f3c2a",
  "nome": "Ana Souza",
  "email": "ana@exemplo.com",
  "nivel_atual": "Iniciante"
}
```

**`POST /auth/login`**: entrada `{ "email": "...", "senha": "..." }`. Resposta `200`:

```json
{ "access_token": "<jwt>", "token_type": "bearer", "expira_em_segundos": 3600 }
```

**`POST /auth/logout`**: resposta `204`. O token é **sem estado**: o cliente o descarta e ele expira sozinho.

## 4. Documentos

**`POST /documentos`** aceita:

- `multipart/form-data` com o campo `arquivo` (PDF, MD ou TXT), ou
- JSON `{ "titulo": "...", "conteudo": "..." }` para texto bruto.

Resposta `201`:

```json
{
  "documento_id": "doc-91b0",
  "titulo": "Introducao a Arquitetura de Redes VCN na OCI",
  "formato_origem": "pdf",
  "chunks_indexados": 14,
  "nivel_documento_estimado": "Desenvolvedor Junior",
  "status_upload": "concluido"
}
```

`nivel_documento_estimado` pode ser `null` (LLM indisponível na ingestão). `status_upload` pode ser `pendente` ou `falha`: o documento **está indexado e utilizável** mesmo assim.

**`GET /documentos`** devolve a lista com `documento_id`, `titulo`, `formato_origem`, `nivel_documento_estimado`, `status_upload` e `criado_em`.

## 5. Adaptações

### 5.1 Requisição

**`POST /adaptacoes`** mantém **exatamente** os campos do exemplo do edital e acrescenta `documento_id` e opcionais. Informe **ou** `documento_id` **ou** `documento_titulo` + `documento_conteudo`.

```json
{
  "documento_id": null,
  "documento_titulo": "Introducao a Arquitetura de Redes VCN na OCI",
  "documento_conteudo": "A Virtual Cloud Network (VCN) e uma rede privada e personalizavel ...",
  "perfil_destinatario": "Iniciante",
  "formato_saida": "Flashcards",
  "nicho_setor": "Geral",
  "nivel_detalhe": "Didatico",
  "incluir_analogias": false,
  "incluir_microlearning": false
}
```

| Campo | Obrigatório | Valores |
|---|---|---|
| `perfil_destinatario` | Sim | `Iniciante`, `Desenvolvedor Junior`, `Desenvolvedor Pleno`, `Tech Lead`, `Arquiteto`, `Gestor/Executivo` |
| `formato_saida` | Sim | `Tutorial`, `Flashcards`, `Quiz`, `Resumo Executivo`, `Roteiro de Aula` |
| `nicho_setor` | Sim | `Geral`, `Fintech`, `Saude`, `E-commerce` |
| `nivel_detalhe` | Sim | `Didatico`, `Intermediario`, `Aprofundado` |
| `incluir_analogias` | Não (padrão `false` até E8) | booleano |
| `incluir_microlearning` | Não (padrão `false` até E9) | booleano |

Parâmetro de consulta `?incluir_gabarito=true`: para `formato_saida = Quiz`, a resposta **omite** `resposta_correta` e `justificativa` por padrão (o feedback vem do endpoint de respostas). Com `true` (útil na demo e no Swagger) o gabarito é incluído. O JSON guardado no banco e no bucket **sempre** contém o gabarito, e a validação de XP é feita no servidor com base nele.

### 5.2 Resposta `200` (exemplo completo, Flashcards, nicho Geral)

```json
{
  "status": "sucesso",
  "versao_schema": "1.0",
  "request_id": "req-20261017-0001",
  "metadados": {
    "perfil_aplicado": "Iniciante",
    "formato_gerado": "Flashcards",
    "nicho_aplicado": "Geral",
    "nivel_detalhe": "Didatico",
    "tempo_estimado_estudo_minutos": 5,
    "conceitos_chave": ["VCN", "Sub-redes", "Internet Gateway", "Security Lists"],
    "pre_requisitos": ["Nocoes basicas de redes"],
    "nivel_documento_estimado": "Desenvolvedor Pleno",
    "alerta_descompasso": true
  },
  "conteudo_adaptado": {
    "titulo": "Dominando Redes na Nuvem (VCN) do Zero",
    "introducao_contextualizada": "Imagine a VCN como o seu proprio bairro particular e seguro dentro da nuvem da Oracle, onde voce decide quem entra e quem sai.",
    "itens": [
      {
        "frente": "O que e uma VCN na Oracle Cloud?",
        "verso": "E a sua rede virtual privada e personalizada dentro da nuvem da Oracle, funcionando como a infraestrutura de rede da sua empresa.",
        "dica_didatica": "Pense nela como o terreno cercado onde seus servidores moram.",
        "conceito_ref": "VCN",
        "analogia_ref": "an-01",
        "fontes_chunks": ["chunk-001", "chunk-002"]
      }
    ]
  },
  "analogias": [
    {
      "id": "an-01",
      "conceito": "VCN",
      "estrategia": "analogia_cotidiano_inspirada_feynman",
      "analogia": "A VCN funciona como um condominio fechado com portaria e areas comuns.",
      "mapeamento": [
        { "termo_tecnico": "Sub-rede publica", "elemento_analogia": "Area comum aberta aos visitantes" },
        { "termo_tecnico": "Security List", "elemento_analogia": "Lista de visitantes autorizados na portaria" }
      ],
      "limite_da_analogia": "Um condominio tem um unico portao fisico; a VCN pode ter varios gateways e regras por sub-rede.",
      "ancorada_na_fonte": false,
      "conceito_ancorado_em": ["chunk-001"],
      "fontes_externas": []
    }
  ],
  "microlearning": {
    "duracao_total_min": 5,
    "blocos": [
      {
        "ordem": 1,
        "titulo": "O que e uma VCN",
        "duracao_min": 2,
        "itens_ref": [0],
        "objetivo": "Entender a VCN como rede privada"
      }
    ]
  },
  "avaliacao_qualidade": {
    "ancoragem_fonte_score": 0.98,
    "fidelidade_analogias_score": 0.93,
    "clareza_pedagogica": "Alta",
    "chunks_utilizados": 4,
    "observacoes": "Linguagem ajustada com analogias para publico iniciante, sem jargoes excessivos."
  },
  "trilha_evolucao": {
    "nivel_atual": "Iniciante",
    "proximo_nivel": "Desenvolvedor Junior",
    "xp_total": 60,
    "xp_ganho_nesta_sessao": 10,
    "xp_disponivel_ao_validar": 0,
    "xp_para_proximo_nivel": 100,
    "progresso_percentual": 60,
    "conceitos_dominados": ["VCN"],
    "conceitos_em_aprendizado": ["Sub-redes", "Internet Gateway", "Security Lists"],
    "teste_nivel_disponivel": false,
    "limiar_aprovacao": 0.7,
    "sugestao_promocao": false
  },
  "armazenamento_oci": {
    "bucket": "AdaptAI-conteudos-educativos",
    "objeto_id": "adaptacoes/usr-7f3c2a/conteudo-vcn-iniciante-flashcards-001.json",
    "documento_original_id": "documentos/usr-7f3c2a/doc-91b0/vcn-introducao.md",
    "status_upload": "concluido"
  }
}
```

**Notas sobre o exemplo**

- `analogias`, `microlearning` e `trilha_evolucao` aparecem como `null` até os épicos E8, E9 e E7 serem entregues.
- `xp_ganho_nesta_sessao` reflete o XP de **geração** (RN-03). `xp_disponivel_ao_validar` é o potencial de XP ao responder o quiz (RN-04): **só o formato Quiz oferece XP de validação**, então vale 0 em Flashcards (como neste exemplo) e, em um Quiz de 6 perguntas, valeria 30.
- `xp_para_proximo_nivel` é o **XP acumulado** necessário para liberar o Teste de Nível (o limiar do nível, RN-05), e `progresso_percentual` é `xp_total / xp_para_proximo_nivel`. Neste exemplo: 60 de 100, ou seja, 60%.
- `alerta_descompasso` é `true` aqui porque o documento foi estimado em Pleno e o usuário é Iniciante, uma diferença de 2 degraus (RN-09). Com `nivel_documento_estimado = null`, o alerta é sempre `false`.
- `introducao_contextualizada` e `dica_didatica` usam linguagem figurada, o que é permitido (RN-19): o juiz de fidelidade avalia apenas afirmações factuais. Analogias com mapeamento ficam em `analogias`.
- `armazenamento_oci.status_upload` pode ser `pendente` ou `falha`; o resultado já está no banco e pode ser reaberto por `GET /adaptacoes/{id}` (RN-17).
- Os valores de XP, limiares e percentuais são **ilustrativos** e vêm da configuração.

### 5.3 Estrutura dos `itens` por formato

| Formato | Campos de cada item |
|---|---|
| Flashcards | `frente`, `verso`, `dica_didatica`, `conceito_ref`, `analogia_ref?`, `fontes_chunks` |
| Quiz | `pergunta`, `alternativas[{id, texto}]`, `resposta_correta`, `justificativa`, `conceito_ref`, `analogia_ref?`, `fontes_chunks` |
| Tutorial | `passo`, `titulo`, `instrucao`, `exemplo?`, `conceito_ref`, `fontes_chunks` |
| Resumo Executivo | `topico`, `resumo`, `impacto_negocio`, `conceito_ref`, `fontes_chunks` |
| Roteiro de Aula | `bloco`, `titulo`, `fala`, `duracao_min`, `recurso_visual?`, `conceito_ref`, `fontes_chunks` |

`?` indica campo opcional. A introdução e o título ficam em `conteudo_adaptado` para todos os formatos.

### 5.4 Listagem e reabertura

**`GET /adaptacoes`** devolve um resumo lido do banco, sem o JSON completo, com paginação simples (`?limite=20&deslocamento=0`):

```json
{
  "itens": [
    {
      "adaptacao_id": "ada-33de",
      "documento_id": "doc-91b0",
      "titulo": "Dominando Redes na Nuvem (VCN) do Zero",
      "perfil_aplicado": "Iniciante",
      "formato_gerado": "Flashcards",
      "nicho_aplicado": "Geral",
      "ancoragem_fonte_score": 0.98,
      "status_upload": "concluido",
      "criado_em": "2026-10-17T14:02:11-03:00"
    }
  ],
  "total": 1
}
```

**`GET /adaptacoes/{adaptacao_id}`** devolve o JSON completo da seção 5.2, exatamente como foi gerado, lido do banco. Para `Quiz`, o gabarito segue a regra de `?incluir_gabarito`.

## 6. Resposta de quiz e XP

**`POST /adaptacoes/{adaptacao_id}/respostas`**

```json
{ "respostas": [ { "item_indice": 0, "alternativa_escolhida": "b" } ] }
```

Resposta `200`:

```json
{
  "acertos": 1,
  "total": 1,
  "xp_ganho": 5,
  "feedback": [
    {
      "item_indice": 0,
      "correta": true,
      "justificativa": "A VCN e a rede virtual privada do cliente dentro da OCI."
    }
  ],
  "trilha_evolucao": { "nivel_atual": "Iniciante", "xp_total": 65, "teste_nivel_disponivel": false }
}
```

Um acerto concede XP **uma vez** por pergunta e adaptação (RN-04), garantido por índice único no banco. Reenviar a mesma resposta retorna `xp_ganho: 0` para itens já pontuados.

## 7. Perfil e Teste de Nível

**`GET /perfil`** retorna o objeto `trilha_evolucao` (formato da seção 5.2), acrescido de `historico` resumido.

**`POST /testes-nivel`** (sem corpo) retorna `201`:

```json
{
  "teste_id": "tst-0a12",
  "nivel_avaliado": "Iniciante",
  "tentativa": 1,
  "perguntas": [
    {
      "id": "q1",
      "pergunta": "Qual componente funciona como a 'portaria' que filtra o trafego da sub-rede?",
      "alternativas": [
        { "id": "a", "texto": "Security List" },
        { "id": "b", "texto": "Internet Gateway" }
      ],
      "conceito_ref": "Security Lists"
    }
  ]
}
```

**`POST /testes-nivel/{teste_id}/respostas`**: entrada `{ "respostas": [ { "pergunta_id": "q1", "alternativa_escolhida": "a" } ] }`. Resposta `200`:

```json
{
  "percentual_dominio": 0.83,
  "aprovado": true,
  "nivel_atual": "Desenvolvedor Junior",
  "conceitos_fracos": [],
  "feedback": [ { "pergunta_id": "q1", "correta": true, "justificativa": "..." } ]
}
```

Reprovado: `aprovado: false`, `nivel_atual` inalterado e `conceitos_fracos` preenchido. Uma nova chamada a `POST /testes-nivel` gera perguntas diferentes (RN-07).

## 8. Erros

Formato único, sempre com mensagem amigável em PT-BR e sem stack trace:

```json
{
  "status": "erro",
  "codigo": "FORMATO_NAO_SUPORTADO",
  "mensagem": "Este tipo de arquivo nao e suportado. Envie um PDF, Markdown ou TXT.",
  "detalhes": [],
  "request_id": "req-20261017-0002"
}
```

| HTTP | `codigo` | Quando |
|---|---|---|
| 400 | `REQUISICAO_INVALIDA` | Corpo malformado ou campos conflitantes (ex.: `documento_id` e conteúdo juntos) |
| 401 | `NAO_AUTENTICADO` | Token ausente ou inválido |
| 401 | `TOKEN_EXPIRADO` | Token vencido |
| 401 | `CREDENCIAIS_INVALIDAS` | E-mail ou senha incorretos |
| 404 | `RECURSO_NAO_ENCONTRADO` | Recurso inexistente **ou de outro usuário** |
| 409 | `EMAIL_JA_CADASTRADO` | Cadastro com e-mail existente |
| 409 | `TESTE_NIVEL_INDISPONIVEL` | XP abaixo do limiar do nível |
| 413 | `ARQUIVO_MUITO_GRANDE` | Acima do limite de upload |
| 415 | `FORMATO_NAO_SUPORTADO` | Tipo de arquivo não aceito |
| 422 | `VALIDACAO_FALHOU` | Falha de validação Pydantic (com `detalhes` por campo) |
| 422 | `DOCUMENTO_SEM_TEXTO` | PDF digitalizado sem texto extraível |
| 422 | `CONCEITOS_INSUFICIENTES` | Menos de 3 conceitos no nível para montar o Teste de Nível |
| 502 | `LLM_INDISPONIVEL` | Falha ou limite do provedor de LLM |
| 503 | `BANCO_INDISPONIVEL` | Falha de acesso ao banco de dados |
| 503 | `ARMAZENAMENTO_INDISPONIVEL` | Operação que **depende** do bucket e não pode seguir sem ele (por exemplo, reindexação a partir do original). No fluxo normal de geração, falha no bucket vira `status_upload = "falha"`, não erro |
| 504 | `TEMPO_ESGOTADO` | Geração acima do tempo máximo |

## 9. Segurança do contrato

- O `usuario_id` **nunca** é aceito no corpo ou na URL de rotas do usuário: sempre vem do token.
- `senha_hash` e dados de outros usuários jamais aparecem em respostas.
- Respostas de erro não revelam se um recurso existe para outro usuário (sempre 404).
