#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create namespace

export NAMESPACE="codedx"

./kube-apply.py "namespace.yaml"

# Generate secrets

export SERVICE="${NAMESPACE}"
export SERVICE_SECRET="${SERVICE}"

./gen-secret.sh "${SERVICE_SECRET}" \
  DB_PASSWORD 32 \
  SUPERUSER_PASSWORD 32

# Deploy the service

export SERVICE_ACCOUNT="${NAMESPACE}"
export SERVICE_DISK="${NAMESPACE}"
export SERVICE_VOLUME="${SERVICE}"
export STATEFUL_SET="${SERVICE}"

export DB_NAME="${SERVICE}"
export DB_USER="${SERVICE}"

export SQL_REGION="us-east1"
export SQL_INSTANCE="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./volume.sh

./kube-apply.py \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py \
  "ingress.yaml"
