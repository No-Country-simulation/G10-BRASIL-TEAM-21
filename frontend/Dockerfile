# Servidor de desenvolvimento do Vite (uso local e demonstração via Compose).
# Requer package.json e package-lock.json em frontend/ (gere com "npm create vite@latest" e "npm install").
FROM node:26-alpine

WORKDIR /app

# Dependências primeiro: a camada fica em cache enquanto o package*.json não mudar.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Sem privilégios de root. node_modules pertence ao usuário "node".
RUN chown -R node:node /app
USER node

EXPOSE 5173
# --host é obrigatório: sem ele o Vite escuta só em localhost, dentro do container.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
