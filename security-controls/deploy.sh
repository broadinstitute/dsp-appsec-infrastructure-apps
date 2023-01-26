#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export SERVICE_SECRET="${NAMESPACE}"
export SC_FIRESTORE_COLLECTION="security-controls"
export SERVICE="${NAMESPACE}-trigger-daily"
export SERVICE_ACCOUNT="${NAMESPACE}"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"
