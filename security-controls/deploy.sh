#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="security-controls"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml"

export SERVICE="${NAMESPACE}"
export CRON_JOB="${NAMESPACE}-trigger-weekly"
export SERVICE_ACCOUNT="${CRON_JOB}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"
