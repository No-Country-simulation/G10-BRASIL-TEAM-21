FROM nginx:alpine

# Remove a configuração padrão para evitar conflitos ("Welcome to nginx")
RUN rm /etc/nginx/conf.d/default.conf

# Copia a sua configuração de proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf
