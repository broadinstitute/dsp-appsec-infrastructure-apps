#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create namespace

export NAMESPACE="defectdojo"

kubectl create namespace "${NAMESPACE}" || true

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

export PROJECT_ID="$(gcloud config get-value project)"

export DEPLOYMENT="${NAMESPACE}"
export SERVICE_ACCOUNT="${NAMESPACE}"

export ADMIN_CONFIG="admin"
export CELERY_CONFIG="celery"
export DJANGO_CONFIG="django"

export DD_DATABASE_USER="postgres"
export DD_DATABASE_PORT="5432"

export SQL_INSTANCE="${NAMESPACE}"
export SQL_REGION="us-east1"

export IP_NAME="${NAMESPACE}"
export LOCALHOST="127.0.0.1"
export TARGET_PORT="http"

./kube-apply.py "${CWD}/deployment.yaml"
./kube-apply.py "service-account.yaml"
./ingress.sh
