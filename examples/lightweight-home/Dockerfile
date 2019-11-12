FROM nginx:alpine

RUN mkdir -p /srv/www/site
COPY out/ /srv/www/site/

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

