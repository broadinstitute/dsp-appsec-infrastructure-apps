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


# install config connector
gcloud storage cp gs://configconnector-operator/latest/release-bundle.tar.gz release-bundle.tar.gz
tar zxvf release-bundle.tar.gz
kubectl apply -f operator-system/configconnector-operator.yaml

./kube-apply.py \
  "configconnector.yaml" \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "global.yaml"
