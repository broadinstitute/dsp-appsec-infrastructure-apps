#!/usr/bin/env bash

set -euo pipefail

# parse global vars from Terraform
export $(xargs < .env)

# get cluster credentials
gcloud container clusters get-credentials --region "${region}" "${cluster}"

# deploy global resources
export NAMESPACE="${GLOBAL_NAMESPACE}"
# export PSP_NAME="restricted"
export PSP_ROLE="${NAMESPACE}-psp"
export PSP_BINDING="${PSP_ROLE}"


./kube-apply.py \
  "configconnector.yaml" \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "global.yaml"
