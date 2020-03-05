#!/usr/bin/env bash

# Install Config Connector (Cloud Native Resource Management)

set -euo pipefail

SA_EMAIL="$1"

# wait for CNRM initialization, or exit if already initialized
kubectl wait pod cnrm-controller-manager-0 \
  -n cnrm-system --for=condition=Initialized || exit 0

# work in a temp directory
cd "$(mktemp -d)"

# download and patch Kubernetes config for CNRM
gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
cd "install-bundle-workload-identity"
sed -Ei.bak "s/(gcp-service-account: ).*/\1${SA_EMAIL}/" "0-cnrm-system.yaml"

# apply the config
kubectl apply -f .
