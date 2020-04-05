#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="sdarq"
export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE_ACCOUNT="${NAMESPACE}"
export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"

export SDARQ_CONFIG="${SERVICE}"
export SDARQ_SECRET="sdarq"

export FRONTEND_PORT="frontend"
export BACKEND_PORT="backend"

./kube-apply.py \
  "namespace.yaml" \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py "${CWD}/ingress.yaml"
