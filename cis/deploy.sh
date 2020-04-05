#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="cis"

./kube-apply.py \
  "namespace.yaml" \
  "${CWD}/deployment.yaml"
