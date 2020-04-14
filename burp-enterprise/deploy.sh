#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create namespace

export NAMESPACE="burp-enterprise"

./kube-apply.py "namespace.yaml"

# Deploy the service

export SERVICE="${NAMESPACE}"

export SERVICE_ACCOUNT="${NAMESPACE}"
export DEPLOYMENT="${SERVICE}"

export SECRET_CONFIG="${SERVICE}"
export SECRET_CONFIG_VOLUME="${SECRET_CONFIG}"

export DB_NAME="${SERVICE}"
export DB_PORT="3306"

export DB_SECRET="${SERVICE}-db"
export DB_USER="burpsuite"

./gen-secret.sh "${DB_SECRET}" \
  DB_PASSWORD 32

DB_PASSWORD=$(
  kubectl get secret "${DB_SECRET}" -n "${NAMESPACE}" \
    -o jsonpath='{.data.DB_PASSWORD}' | base64 --decode
)
export DB_PASSWORD

export SQL_REGION="us-east1"
export SQL_INSTANCE="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

export BURP_VERSION="1.1.04"

./kube-apply.py \
  "secret-config.yaml" \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py \
  "ingress.yaml"
