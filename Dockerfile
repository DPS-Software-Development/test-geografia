FROM nginx:alpine

# Replace the default site with one that listens on $PORT (Railway convention).
# nginx:alpine's docker-entrypoint runs envsubst on /etc/nginx/templates/*.template at startup.
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY index.html /usr/share/nginx/html/index.html

ENV PORT=8080
EXPOSE 8080
