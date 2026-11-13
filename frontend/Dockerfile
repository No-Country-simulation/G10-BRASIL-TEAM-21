# ESTÁGIO 1: Build do React/Vite
FROM node:26-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Recebe a URL da API na hora do build (padrão para chamadas relativas)
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ESTÁGIO 2: Servir os arquivos estáticos com Nginx
FROM nginx:alpine
# Remove a config padrão do Nginx do container do front
RUN rm /etc/nginx/conf.d/default.conf
# Copia os arquivos compilados do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
