#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="${CIS_NAMESPACE}"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"
