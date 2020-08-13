#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="zap"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh
