#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export SERVICE="${NAMESPACE}"
export SERVICE_SECRET="${NAMESPACE}"
export CRON_JOB="${NAMESPACE}-trigger-daily"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export SERVICE_ACCOUNT="${CRON_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"
