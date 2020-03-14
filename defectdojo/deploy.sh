#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="defectdojo"

./kube-apply.py "namespace.yaml"

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

export SERVICE="${NAMESPACE}"
export SERVICE_ACCOUNT="${NAMESPACE}"
export STATEFUL_SET="${SERVICE}"
export MEDIA_VOLUME="media"

export ADMIN_CONFIG="admin"
export CELERY_CONFIG="celery"
export DJANGO_CONFIG="django"

export DD_DATABASE_USER="postgres"
export DD_DATABASE_PORT="5432"

export SQL_REGION="us-east1"
export SQL_INSTANCE="${NAMESPACE}"
export SQL_INSTANCE_URI="${PROJECT_ID}:${SQL_REGION}:${SQL_INSTANCE}=tcp:${DD_DATABASE_PORT}"

export LOCALHOST="127.0.0.1"
export TARGET_PORT="http"

./kube-apply.py "service-account.yaml" "${CWD}/deployment.yaml"
./ingress.sh
