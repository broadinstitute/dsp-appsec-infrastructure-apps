#!/usr/bin/env sh

export HTTPS_PROXY="socks5://${PROXY_HOST}:${PROXY_PORT}"

kubectl "$@"
