#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="${CIS_NAMESPACE}"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"
