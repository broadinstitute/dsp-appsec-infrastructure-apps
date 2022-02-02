#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

# Create namespace

export NAMESPACE="ramper"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

# Generate secrets

export SERVICE="${NAMESPACE}"
export SERVICE_CONFIG="${SERVICE}"
export DB_SECRET="${SERVICE}"
export EMAIL_SECRET="${SERVICE}-email"

./gen-secret.sh "${DB_SECRET}" \
  MYSQL_ROOT_PASSWORD 32 \
  MYSQL_PASSWORD 32 \

# Deploy the service

export SERVICE_DISK="${NAMESPACE}"
export SERVICE_VOLUME="${SERVICE}"
export STATEFUL_SET="${SERVICE}"

export DB_NAME="${SERVICE}"
export DB_USER="${SERVICE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export FRONTEND_CONFIG="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./volume.sh

./kube-apply.py \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py \
  "${iap_secret_yaml}" \
  "ingress.yaml"
