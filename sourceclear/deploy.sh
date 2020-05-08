#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

python3 render_template.py

export NAMESPACE="sourceclear"
export JOB_TOPIC="${NAMESPACE}-scans"
export JOB_CONFIG_MAP="${JOB_TOPIC}"
export SERVICE_ACCOUNT="${NAMESPACE}"
export SRCCLR_DATASET="cis"
export SRCCLR_TABLE="dsp_appsec_${NAMESPACE}_repos"


./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"

./batch.sh