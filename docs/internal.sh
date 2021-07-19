#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="internal-docs"
export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
# What URL should when have for internal docs
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export FRONTEND_CONFIG="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./kube-apply.py \
    "namespace.yaml" \
    "configconnectorcontext.yaml" \
    "${CWD}/internal.yaml"

./host.sh

./kube-apply.py "${CWD}/ingress.yaml"