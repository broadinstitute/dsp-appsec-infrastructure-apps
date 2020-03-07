#!/usr/bin/env bash

set -euo pipefail

# Create namespace

export NAMESPACE="defectdojo"

kubectl create namespace "${NAMESPACE}" || true

# Generate secrets

export ADMIN_SECRET="admin"
export CELERY_SECRET="celery"
export DJANGO_SECRET="django"

../scripts/gen-secret.sh "${ADMIN_SECRET}" \
  DD_ADMIN_PASSWORD 32

../scripts/gen-secret.sh "${CELERY_SECRET}" \
  DD_CELERY_BROKER_PASSWORD 32

../scripts/gen-secret.sh "${DJANGO_SECRET}" \
  DD_DATABASE_PASSWORD 32 \
  DD_CREDENTIAL_AES_256_KEY 128 \
  DD_SECRET_KEY 128

# Deploy the service

export PROJECT_ID="$(gcloud config get-value project)"

export BACKEND_CONFIG="defectdojo"
export DEPLOYMENT="defectdojo"
export SERVICE="defectdojo"
export SERVICE_ACCOUNT="defectdojo"

export ADMIN_CONFIG="admin"
export CELERY_CONFIG="celery"
export DJANGO_CONFIG="django"

export DD_DATABASE_USER="defectdojo"
export DD_DATABASE_PORT="5432"

export SQL_INSTANCE="defectdojo"
export SQL_REGION="us-east1"

export LOCALHOST="127.0.0.1"

../scripts/kube-apply.py "service.yaml"

# Create Ingress with DNS hostname and Managed Certificate

../scripts/dns-ingress.sh
