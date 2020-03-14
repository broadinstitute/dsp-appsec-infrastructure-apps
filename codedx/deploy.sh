#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
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
export SERVICE_VOLUME="${NAMESPACE}"
export STATEFUL_SET="${SERVICE}"

export DB_NAME="${SERVICE}"
export DB_USER="${SERVICE}"
export DB_PORT="3306"

export SQL_REGION="us-east1"
export SQL_INSTANCE="${NAMESPACE}"

export TARGET_PORT="http"

./volume.sh

./kube-apply.py \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"

./ingress.sh
