#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"
export CRON_JOB="${NAMESPACE}-trigger-weekly"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export SERVICE="${CRON_JOB}"
export SERVICE_ACCOUNT="${CRON_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"
