#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="cis"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export JOB_SECRET="${JOB_CONFIG_MAP}"
export K8S_SERVICE_ACCOUNT="${JOB_CONFIG_MAP}"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh
