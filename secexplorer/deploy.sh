#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="secexplorer"

./kube-apply.py "namespace.yaml"

# Generate secrets

export SERVICE="${NAMESPACE}"
export SERVICE_SECRET="${SERVICE}"

./gen-secret.sh "${SERVICE_SECRET}" \
  NEO4J_PASSWORD 32

export NEO4J_USERNAME="neo4j"

# Create Nginx config

export NGINX_VOLUME="nginx"
export NGINX_CONFIG="nginx"

kubectl create configmap "${NGINX_CONFIG}" \
  -n "${NAMESPACE}" \
  --from-file "${CWD}/nginx.conf" \
  --dry-run -o yaml | kubectl replace -f -

# Deploy the service

export K8S_SERVICE_ACCOUNT="${NAMESPACE}"
export SERVICE_DISK="${NAMESPACE}"
export SERVICE_VOLUME="${SERVICE}"
export STATEFUL_SET="${SERVICE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./volume.sh

./kube-apply.py "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py "ingress.yaml"
