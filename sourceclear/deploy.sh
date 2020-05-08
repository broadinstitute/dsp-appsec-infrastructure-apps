#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

python3 render_template.py

export NAMESPACE="sourceclear"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export SERVICE_ACCOUNT="${NAMESPACE}"


./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh