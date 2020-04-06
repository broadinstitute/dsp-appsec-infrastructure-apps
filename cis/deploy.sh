#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="cis"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export K8S_SERVICE_ACCOUNT="${JOB_TOPIC}"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh
