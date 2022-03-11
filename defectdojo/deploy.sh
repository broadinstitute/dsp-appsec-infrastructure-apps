#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

# Create namespace

export NAMESPACE="${DOJO_NAMESPACE}"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

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

export DD_DATABASE_TYPE="postgres"
export DD_DATABASE_HOST="${LOCALHOST}"
export DD_DATABASE_NAME="${DD_DATABASE_TYPE}"

# set Database URL as required by DefectDojo 2.8+
DD_DATABASE_PASSWORD=$(kubectl get secret "${DJANGO_SECRET}" -n "${NAMESPACE}" --template={{.data.DD_DATABASE_PASSWORD}} | base64 --decode)
DD_DATABASE_URL="${DD_DATABASE_TYPE}://${DD_DATABASE_USER}:${DD_DATABASE_PASSWORD}@${DD_DATABASE_HOST}:${DD_DATABASE_PORT}/${DD_DATABASE_NAME}"
kubectl patch secret "${DJANGO_SECRET}" -n "${NAMESPACE}" -p "{\"data\": {\"DD_DATABASE_URL\":\"$(printf ${DD_DATABASE_URL} | base64 -w0)\"}}"

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
