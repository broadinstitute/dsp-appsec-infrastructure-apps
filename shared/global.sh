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
  "https://raw.githubusercontent.com/broadinstitute/dsp-appsec-infrastructure-apps/eb1c7d0e2f40080cf3448dafef69f979bf37641c/shared/psa.yaml"

./kube-apply.py \
  "configconnector.yaml" \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "global.yaml"
