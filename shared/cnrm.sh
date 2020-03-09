#!/usr/bin/env bash

# Install Config Connector (Cloud Native Resource Management)

set -euo pipefail

SA_EMAIL="$1"

# wait for CNRM initialization, or exit if already initialized
kubectl wait --for condition=Initialized pod \
  cnrm-controller-manager-0 -n cnrm-system && exit 0

# work in a temp directory
cd "$(mktemp -d)"

# download and patch Kubernetes config for CNRM
gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
cd "install-bundle-workload-identity"
git apply "0-cnrm-system.yaml.patch"

# apply the config
kubectl apply -f .

# patch the service account
kubectl annotate serviceaccount -n cnrm-system cnrm-controller-manager \
  "iam.gke.io/gcp-service-account=${SA_EMAIL}"
