# ===========================================================================================================
# 1. Builder stage
# ===========================================================================================================

FROM nexus.oigit.cn/library/node:latest AS html

RUN npm config set registry http://192.168.186.125:8081/repository/npm
RUN yarn config set registry http://192.168.186.125:8081/repository/npm


COPY ./ /usr/html

WORKDIR /usr/html
RUN yarn install && yarn api && yarn build



# ===========================================================================================================
# 2. Deploy stage
# ===========================================================================================================

FROM nexus.oigit.cn/library/nginx:latest

WORKDIR /
COPY --from=html /usr/html/dist /usr/share/nginx/html
COPY --from=html /usr/html/nginx.conf /etc/nginx/conf.d/default.conf.template
COPY --from=html /usr/html/.env /usr/share/nginx/html
COPY --from=html /usr/html/docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

RUN chmod -R 755 /usr/share/nginx/html
RUN nginx -t

CMD ["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"]