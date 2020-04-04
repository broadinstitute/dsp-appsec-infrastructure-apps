#!/usr/bin/env bash

set -euo pipefail

export HTTPS_PROXY="socks5://${PROXY_HOST}:${PROXY_PORT}"

kubectl "$@"
