#!/usr/bin/env bash

# Install Config Connector (CNRM)

set -euo pipefail

CLUSTER_ZONE="$1"
CLUSTER_NAME="$2"
SA_EMAIL="$3"

# get cluster credentials
gcloud container clusters get-credentials --zone "${CLUSTER_ZONE}" "${CLUSTER_NAME}"

# exit if already installed
kubectl get namespace "cnrm-system" && exit 0

(
  # work in a temp directory
  cd "$(mktemp -d)"

  # download and patch Kubernetes config for cnrm
  gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
  cd "install-bundle-workload-identity"
  sed -Ei.bak "s/(gcp-service-account: ).*/\1${SA_EMAIL}/" "0-cnrm-system.yaml"

  # apply the config
  kubectl apply -f .
)
