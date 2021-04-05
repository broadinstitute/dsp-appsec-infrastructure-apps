#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

# Create namespace

export NAMESPACE="secexplorer"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

# Generate secrets

export SERVICE="${NAMESPACE}"
export SERVICE_SECRET="${SERVICE}"

./gen-secret.sh "${SERVICE_SECRET}" \
  NEO4J_PASSWORD 32

export NEO4J_USERNAME="neo4j"

# Deploy Nginx config

export NGINX_VOLUME="nginx"
export NGINX_CONFIG="nginx"

kubectl create configmap "${NGINX_CONFIG}" \
  -n "${NAMESPACE}" \
  --from-file "${CWD}/nginx.conf" \
  --dry-run -o yaml | kubectl apply -f -

# Deploy the service

export K8S_SERVICE_ACCOUNT="${NAMESPACE}"
export SERVICE_DISK="${NAMESPACE}"
export SERVICE_VOLUME="${SERVICE}"
export STATEFUL_SET="${SERVICE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export FRONTEND_CONFIG="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export HTTP_PORT="http"
export BOLT_PORT="bolt"

./volume.sh

./kube-apply.py "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py \
  "${iap_secret_yaml}" \
  "${CWD}/ingress.yaml"
