#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="docs"
export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py "${CWD}/ingress.yaml"
