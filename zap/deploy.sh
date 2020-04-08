#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="zap"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"

./batch.sh
