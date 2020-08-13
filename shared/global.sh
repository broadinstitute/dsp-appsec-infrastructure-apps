#!/usr/bin/env bash

set -euo pipefail

# get cluster credentials
gcloud container clusters get-credentials --region "${region}" "${cluster}"

# deploy global resources using Config Connector
export NAMESPACE="${GLOBAL_NAMESPACE}"

./kube-apply.py \
  "namespace.yaml" \
  "global.yaml"
