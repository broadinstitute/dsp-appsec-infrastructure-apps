#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="srcclr"
export CRON_JOB="${NAMESPACE}-trigger"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"
export DEFECT_DOJO_URL="http://${DOJO_SERVICE}.${DOJO_NAMESPACE}.svc.cluster.local"

./kube-apply.py \
    "namespace.yaml" \
    "configconnectorcontext.yaml"

export SERVICE="${CRON_JOB}"
export SERVICE_ACCOUNT="${CRON_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

./kube-apply.py "${CWD}/deployment.yaml"

./batch.sh
