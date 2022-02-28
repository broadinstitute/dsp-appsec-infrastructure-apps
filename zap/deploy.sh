#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="zap"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export JOB_SECRET="${JOB_CONFIG_MAP}"
export JOB_SERVICE_ACCOUNT="${JOB_CONFIG_MAP}"
export CRON_JOB="${NAMESPACE}-trigger"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"
export CODEDX_URL="http://${CODEDX_SERVICE}.${CODEDX_NAMESPACE}.svc.cluster.local/codedx"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export ZAP_PORT='8008'
export BUCKET_NAME="${PROJECT_ID}-vuln-reports"
export SESSION_BUCKET="${PROJECT_ID}-zap-sessions"
export VOLUME_SHARE="/tmp/share"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export SERVICE="${JOB_CONFIG_MAP}"
export SERVICE_ACCOUNT="${JOB_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

export SERVICE="${CRON_JOB}"
export SERVICE_ACCOUNT="${CRON_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"

./batch.sh
