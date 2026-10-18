# ADR-0015 — Docker Compose, backend único e VM como bônus

- **Status:** Aceito
- **Data:** 2026-10-17
- **Decisores:** Equipe AdaptAI (Grupo 10)

## Contexto

O diagrama de arquitetura da equipe coloca todos os componentes em um Docker Compose na raiz do monorepo, dentro de uma OCI Compute. Ele separa visualmente "API FastAPI", "Backend" e "Serviço RAG". O edital exige apenas o OCI Object Storage; a hospedagem na Compute é **diferencial opcional**.

Duas decisões precisam ficar explícitas: se essas caixas são processos separados e onde a demonstração principal roda.

## Decisão

1. **Monorepo único**, com `backend/`, `frontend/` e `docs/` no mesmo repositório.
2. **Um `docker-compose.yml` na raiz**, com três serviços: `db` (PostgreSQL com `pgvector`), `backend` (FastAPI) e `frontend` (build estático servido por um servidor web leve).
3. **Backend único.** API, regras de serviço, grafo LangGraph e o pipeline RAG são **módulos do mesmo processo Python**, separados por camadas lógicas (`api`, `services`, `agents`, `rag`, `ports`, `infra`). Não há serviço RAG separado nem chamada de rede entre eles.
4. **A demonstração principal roda localmente** com `docker compose up`. A **OCI Compute é bônus** (US-093), entra tarde no cronograma e reaproveita o mesmo Compose. Se falhar, a demonstração não depende dela.
5. **Rede:** o Postgres não é exposto fora da rede do Compose. Na VM, só as portas do front-end e da API ficam abertas, por regra de segurança da VCN.
6. **Segredos:** `.env` fora do Git, também na VM. Avaliar *instance principals* para a autenticação na OCI sem chave de API na VM, o que exige uma política de IAM. Confirmar no spike.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Serviço RAG em container separado | Acrescenta fronteira de rede, serialização, mais um ponto de falha e mais deploy, sem benefício de escala para o MVP |
| Hospedar na VM como alvo principal | Depende de conta, região e capacidade que a equipe não controla; ver riscos abaixo |
| Sem Compose (processos soltos) | Perde a paridade entre desenvolvimento, demonstração e VM |

## Consequências

**Positivas**
- Um único processo de backend simplifica depuração, testes e deploy.
- `docker compose up` sobe a stack inteira em qualquer máquina, inclusive a de quem avalia.
- Se a VM falhar, existe plano B imediato.

**Negativas e riscos**
- O RAG não escala separadamente. Aceitável para o MVP.
- Chamadas lentas ao LLM exigem rotas assíncronas ou *threadpool* (ver [ADR-0001](./ADR-0001-python-e-fastapi-no-backend.md)).
- O modelo local de embeddings (ADR-0011) fica dentro da imagem do backend e aumenta memória e tamanho da imagem.
- **Dimensionamento da VM Always Free** (conferir a documentação vigente da Oracle):
  - A VM AMD (`VM.Standard.E2.1.Micro`) tem 1 GB de memória. Não comporta banco, backend com embeddings e front-end juntos.
  - A VM Arm (`VM.Standard.A1.Flex`) oferece até 4 OCPUs e 24 GB no total, alocáveis de forma flexível. Cabe, mas exige imagens e dependências compatíveis com **arm64**, e a criação pode falhar por falta de capacidade na região.
  - Instâncias Always Free ociosas podem ser recuperadas pela Oracle. Entre a primeira entrega e a fase final pode haver dias sem uso.
  - Os serviços Always Free só rodam na **região principal** escolhida no cadastro da conta, que não pode ser alterada depois.
- Hipótese não medida: o consumo de memória do conjunto. Medir antes de apostar na VM.

## Referências
[04 - Arquitetura](../04%20-%20Arquitetura.md#12-execução-e-implantação) · US-007, US-093 · [Recursos Always Free da OCI](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm)
