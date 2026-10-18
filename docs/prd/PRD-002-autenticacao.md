# PRD-002 — Autenticação simples

- **Status:** Aprovado (revisado em 2026-10-17)
- **Prioridade:** MVP (semana 2)
- **Requisitos relacionados:** RF-01, RF-02, RF-03 · RN-01, RN-14 · RNF-02
- **Épico:** E6 · **ADR:** [ADR-0006](../adr/ADR-0006-autenticacao-jwt-simples.md) e [ADR-0013](../adr/ADR-0013-postgresql-como-banco-de-leitura.md) (armazenamento)

## 1. Resumo

Cadastro, login e logout com e-mail e senha. Existe para dar **identidade** ao usuário e permitir o histórico e o perfil de evolução. Escopo mínimo: **sem recuperação de senha e sem OAuth**.

## 2. Problema

A evolução do usuário (XP, nível, conceitos) e o histórico de adaptações precisam estar ligados a uma pessoa. Um sistema sem login não consegue manter esse histórico e passa uma imagem de produto inacabado.

## 3. Objetivos e não objetivos

**Objetivos:** cadastro com nível declarado; login seguro; logout; isolamento total de dados entre usuários.

**Não objetivos:** recuperação de senha, login social, verificação de e-mail, papéis e permissões, autenticação em duas etapas, limite de tentativas (desejável, se sobrar tempo).

**Decisão de produto:** autenticação **não consta do checklist da banca**, mas a equipe a manteve no MVP, na semana 2. Como depende só do banco e das migrações (US-007 e US-008), não disputa tempo com o grafo e a fidelidade da semana 3.

## 4. Usuários e cenários

- **Novo usuário:** cria a conta, escolhe seu nível (Iniciante a Arquiteto) e entra.
- **Usuário recorrente:** faz login e vê seu histórico e nível.
- **Avaliador da banca:** usa o usuário de demonstração criado pelo seed.

## 5. Requisitos e regras

| Item | Regra |
|---|---|
| Cadastro | Nome, e-mail, senha e `nivel_declarado`. E-mail normalizado e único, garantido por índice único no banco (409 se repetido) |
| Senha | Mínimo de 8 caracteres. Hash com bcrypt. Nunca em texto puro, respostas ou logs (RN-14) |
| Login | E-mail e senha corretos retornam JWT com expiração (padrão 60 min). Erro genérico `CREDENCIAIS_INVALIDAS`, sem revelar qual campo falhou |
| Logout | O cliente descarta o token e volta ao login. Resposta `204` |
| Autorização | O `usuario_id` vem **sempre do token**. Toda consulta filtra por ele. Recurso de outro usuário retorna 404 |
| Perfil inicial | O cadastro cria a linha em `perfis_evolucao` com `nivel_atual = nivel_declarado` e XP zero, na mesma transação do usuário |
| Demonstração | Script de seed cria o usuário demo e está no README |

## 6. Critérios de aceite

1. Cadastro com e-mail novo retorna 201; com e-mail repetido, 409 `EMAIL_JA_CADASTRADO`.
2. A senha armazenada é um hash bcrypt (verificável na linha do banco).
3. Login válido retorna token; inválido retorna 401 sem indicar o campo errado.
4. Rotas protegidas retornam 401 sem token e `TOKEN_EXPIRADO` com token vencido.
5. Um usuário não consegue ler documentos ou adaptações de outro (404, teste automatizado).
6. Logout leva ao login e o token descartado não é mais usado pelo front.
7. O usuário demo funciona seguindo apenas o README.

## 7. Métricas de sucesso

Fluxo completo (cadastro, login, uso, logout) em menos de 1 minuto; zero vazamento de dados entre usuários nos testes.

## 8. Dependências e riscos

- Depende de: banco e migrações (US-007, US-008) e contrato (US-002).
- É **pré-requisito** de XP e perfil (E7).
- **Riscos:** o front-end ainda não tem responsável nem framework definido (ADR-0012), e as telas de login estão na semana 2; token roubado válido até expirar. Mitigações: decidir o ADR-0012 no início da semana 1 e expiração curta (ver ADR-0006).

## 9. Perguntas em aberto

1. Onde o front guarda o token (memória, `sessionStorage` ou `localStorage`)? Decidir junto com o [ADR-0012](../adr/ADR-0012-framework-do-front-end.md), avaliando o risco de XSS.
2. Haverá limite de tentativas de login em v1?
