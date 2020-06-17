#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="automated-cis"
export SERVICE_ACCOUNT="${WEEKLY_CIS_SERVICE_ACCOUNT}"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

