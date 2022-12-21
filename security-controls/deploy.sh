#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export SERVICE_SECRET="${NAMESPACE}"
export SERVICE="${NAMESPACE}-trigger-daily"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export SERVICE_ACCOUNT="${SERVICE}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"
