#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export SERVICE_SECRET="${NAMESPACE}"
export SC_FIRESTORE_COLLECTION="security-controls"
export SAST_FIRESTORE_COLLECTION="sast-details"
export SERVICE="${NAMESPACE}-trigger-daily"
export SERVICE_ACCOUNT="${NAMESPACE}"

export CODACY_HOST="https://app.codacy.com"
export SONARCLOUD_HOST="https://sonarcloud.io/api"
export GITHUB_GQL_ENDPOINT="https://api.github.com/graphql"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"
