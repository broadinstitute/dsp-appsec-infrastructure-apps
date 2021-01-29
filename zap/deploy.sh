#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="zap"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export JOB_SECRET="${JOB_CONFIG_MAP}"
export K8S_SERVICE_ACCOUNT="${JOB_CONFIG_MAP}"
export CODEDX_URL="http://${CODEDX_NAMESPACE}.${CODEDX_SERVICE}.svc.cluster.local/codedx"
export DEFECT_DOJO_URL="http://${DOJO_NAMESPACE}.${DOJO_SERVICE}.svc.cluster.local"
export ZAP_PORT='8008'
export BUCKET_NAME="${PROJECT_ID}-vuln-reports"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh
