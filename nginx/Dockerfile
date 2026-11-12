FROM nginx:alpine

# Remove a configuração padrão para evitar conflitos
RUN rm /etc/nginx/conf.d/default.conf

# Copia a sua configuração
COPY nginx.conf /etc/nginx/conf.d/default.conf
