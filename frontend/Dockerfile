# Etapa 1: Build (Compila o React/Vite)
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2: Export (Apenas copia os arquivos gerados)
FROM alpine:latest
WORKDIR /app
COPY --from=build /app/dist ./dist
# Esse comando mantém o container vivo para o volume funcionar
CMD ["sh", "-c", "cp -r /app/dist/. /usr/share/nginx/html/ && tail -f /dev/null"]
