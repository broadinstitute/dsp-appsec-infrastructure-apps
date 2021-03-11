#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="cis"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export JOB_SECRET="${JOB_CONFIG_MAP}"
export JOB_SERVICE_ACCOUNT="${JOB_CONFIG_MAP}"
export CRON_JOB="${NAMESPACE}-trigger-weekly"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"

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
