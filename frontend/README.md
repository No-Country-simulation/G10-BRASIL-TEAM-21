# Frontend (React + Vite)

Framework decidido no [ADR-0012](../docs/adr/ADR-0012-framework-do-front-end.md): React com Vite.
TypeScript ou JavaScript ainda a registrar no ADR.

## Criar o projeto (uma vez, por quem for tocar o front)

Dentro desta pasta, com Node 20 ou superior:

```bash
npm create vite@latest . -- --template react-ts    # ou react, se for JavaScript
npm install
```

Responda "ignore" se perguntar sobre arquivos existentes: `mocks/`, `Dockerfile` e `.dockerignore` ficam.
**Commite `package.json` e `package-lock.json`.** O `Dockerfile` usa `npm ci`, que exige o lock, e o
serviço `frontend` do `docker-compose.yml` falha no build sem eles.

## Rodar

Pelo Compose, na raiz: `docker compose up --build` e abra `http://localhost:5173`.
Direto na máquina: `npm run dev`.

A URL da API vem de `VITE_API_URL` (no Compose, `http://localhost:8000/api/v1`). Em código Vite:
`import.meta.env.VITE_API_URL`.

## Mocks e protótipo

O front é a última camada a ser validada. A primeira versão pode ser um protótipo (inclusive gerado por
IA) que consome os JSONs de `mocks/`, sem backend. Importe-os de dentro de `src/` (copie ou use um alias),
pois o Vite só empacota o que está dentro do projeto. Quando a API existir, troque o mock pela chamada
real: o formato é o mesmo (`docs/05 - Contrato de API.md`).

Telas previstas: cadastro e login, envio de documento, escolha de perfil/formato/nicho, visualização
dos cinco formatos, histórico, trilha de evolução e Teste de Nível.

## Pendente

- Job de front no CI (a cargo do DevOps; esboço em `docs/ci-sugestao/ci.yml.txt`).
- Imagem de produção (build estático servido por nginx) só se o front for implantado na OCI.
- Escolha entre TypeScript e JavaScript, registrada no ADR-0012.
