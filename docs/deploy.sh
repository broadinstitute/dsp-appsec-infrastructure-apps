#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="docs"
export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"

export DOCS_PORT="docs"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py "${CWD}/ingress.yaml"
