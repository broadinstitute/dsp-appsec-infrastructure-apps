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

# kubectl apply -f \
#   "https://raw.githubusercontent.com/kubernetes/website/main/content/en/examples/policy/${PSP_NAME}-psp.yaml"

kubectl apply -f \
  "https://raw.githubusercontent.com/broadinstitute/dsp-appsec-infrastructure-apps/shared/restricted-psp.yaml"

./kube-apply.py \
  "psp.yaml" \
  "configconnector.yaml" \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "global.yaml"
