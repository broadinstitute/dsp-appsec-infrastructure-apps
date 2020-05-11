#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="sourceclear"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export SERVICE_ACCOUNT="${NAMESPACE}"

./kube-validate.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"