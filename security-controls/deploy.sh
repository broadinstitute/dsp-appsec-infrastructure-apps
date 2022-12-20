#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"
export SERVICE="${NAMESPACE}"
export SERVICE_SECRET="${NAMESPACE}"
export CRON_JOB="${NAMESPACE}-trigger-daily"
export SERVICE_ACCOUNT="${CRON_JOB}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"
