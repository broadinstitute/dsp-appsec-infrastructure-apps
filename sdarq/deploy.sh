#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="sdarq"

./kube-apply.py "namespace.yaml"

export SDARQ_SECRET="sdarq"

# Deploy the service

export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SDARQ_CONFIG="${SERVICE}"
export FRONTEND_PORT="frontend"
export BACKEND_PORT="backend"

./kube-apply.py "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py "${CWD}/ingress.yaml"
