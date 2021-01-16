#!/usr/bin/env bash

set -euo pipefail

# parse global vars from Terraform
export $(xargs < .env)

# get cluster credentials
https_proxy= gcloud container clusters get-credentials --region "${region}" "${cluster}"

# deploy global resources using Config Connector
export NAMESPACE="${GLOBAL_NAMESPACE}"

./kube-apply.py \
  "configconnector.yaml" \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "global.yaml"
