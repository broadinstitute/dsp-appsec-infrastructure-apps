#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

# Create namespace

export NAMESPACE="${DOJO_NAMESPACE}"

./kube-apply.py \
  "namespace.yaml"

# Generate secrets

export ADMIN_SECRET="admin"
export CELERY_SECRET="celery"
export DJANGO_SECRET="django"

./gen-secret.sh "${ADMIN_SECRET}" \
  DD_ADMIN_PASSWORD 32

./gen-secret.sh "${CELERY_SECRET}" \
  DD_CELERY_BROKER_PASSWORD 32

./gen-secret.sh "${DJANGO_SECRET}" \
  DD_DATABASE_PASSWORD 32 \
  DD_CREDENTIAL_AES_256_KEY 128 \
  DD_SECRET_KEY 128

# Deploy the service

export SERVICE="${DOJO_SERVICE}"
export SERVICE_ACCOUNT="${NAMESPACE}"
export SERVICE_DISK="${NAMESPACE}"
export SERVICE_VOLUME="${SERVICE}"
export STATEFUL_SET="${SERVICE}"

export ADMIN_CONFIG="admin"
export CELERY_CONFIG="celery"
export DJANGO_CONFIG="django"

export DD_DATABASE_USER="postgres"
export DD_DATABASE_PORT="5432"

export SQL_REGION="us-east1"
export SQL_INSTANCE="${NAMESPACE}"
export SQL_INSTANCE_URI="${PROJECT_ID}:${SQL_REGION}:${SQL_INSTANCE}=tcp:${DD_DATABASE_PORT}"
export SQL_VERSION="POSTGRES_11"
export SQL_TIER="db-custom-1-3840"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"
export LOCALHOST="127.0.0.1"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export FRONTEND_CONFIG="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

./volume.sh

./kube-apply.py \
  "service-account.yaml" \
  "${CWD}/deployment.yaml" \
  "sql.yaml"

./host.sh

./kube-apply.py \
  "${iap_secret_yaml}" \
  "ingress.yaml"
