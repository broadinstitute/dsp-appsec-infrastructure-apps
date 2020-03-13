#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="sdarq"

./namespace.sh

# Generate secrets

export SDARQ_SECRET="sdarq"

./gen-secret.sh "${SDARQ_SECRET}" \
  host 32 \
  user 32 \
  api_key 32 \
  slack_token 32 \
  jira_username 32 \
  jira_api_token 32 \
  jira_instance 32 

# Deploy the service

export DEPLOYMENT="${NAMESPACE}"
export SERVICE_ACCOUNT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export LOCALHOST="127.0.0.1"
export TARGET_PORT="http"

./kube-apply.py "service-account.yaml" "${CWD}/deployment.yaml"
./ingress.sh
