#!/usr/bin/env sh
set -eu

set -o allexport; . /usr/share/nginx/html/.env; set +o allexport;

envsubst '${VITE_PROXY_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

exec "$@"