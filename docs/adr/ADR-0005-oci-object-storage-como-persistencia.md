# ADR-0005 — OCI Object Storage como persistência única

- **Status:** Substituído por [ADR-0013](./ADR-0013-postgresql-como-banco-de-leitura.md)
- **Data:** 2026-10-13
- **Decisores:** Equipe AdaptAI (Grupo 10)

## Contexto

A integração com o **OCI Object Storage (Always Free)** é requisito obrigatório para guardar os documentos originais e os JSONs gerados. O programa ONE é gratuito para os alunos: **nenhuma configuração pode gerar custo**. Precisamos também persistir usuários e perfis de evolução.

## Decisão

1. **Um único bucket** Always Free (`AdaptAI-conteudos-educativos`), organizado por **prefixos** (`documentos/`, `adaptacoes/`, `perfis/`, `usuarios/`, `indices/email/`, `testes_nivel/`).
2. Acesso sempre por uma interface `StoragePort`, com `OCIObjectStorage` (demo e produção) e `LocalFileStorage` (desenvolvimento e testes).
3. **Sem banco de dados** em v1: usuários e perfis são objetos JSON. O login usa um índice por hash do e-mail.
4. Autenticação com o **OCI SDK para Python** por chave de API, configurada por variáveis de ambiente.
5. Respeitar as cotas Always Free; **confirmar que cada novo recurso é Always Free antes de criá-lo**.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Banco de dados (ex.: Autonomous Database Always Free) | Mais robusto para transações, mas aumenta escopo e curva de aprendizado; reavaliar após o hackathon |
| SQLite local | Não cumpre o requisito de persistência no OCI e se perde com a máquina |
| Apenas arquivos locais | Idem |

## Consequências

**Positivas**
- Cumpre o requisito obrigatório com um único serviço e custo zero.
- `LocalFileStorage` destrava o desenvolvimento e os testes sem depender da rede.

**Negativas e riscos**
- **Sem transações:** atualizações de perfil são *ler, alterar e gravar*; em v1 há uma gravação por fluxo e sem concorrência por usuário. Endurecimento opcional com `if-match` (ETag).
- Listagens dependem de prefixos e de objetos de índice.
- Latência e cotas de requisições da camada gratuita. Mitigação: gravar uma vez ao final do fluxo e cachear leituras frequentes.
- Credenciais da OCI são um risco de vazamento. Mitigação: `.env` fora do Git, `.env.example` e revisão de PR ([07 - Convenções](../07%20-%20Conven%C3%A7%C3%B5es.md)).

## Referências
[03 - Modelo de Domínio](../03%20-%20Modelo%20de%20Dom%C3%ADnio.md#6-layout-dos-objetos-no-oci-object-storage) · US-006, US-035, US-036
