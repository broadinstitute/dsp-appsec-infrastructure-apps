#!/usr/bin/env bash

# Install Config Connector (Cloud Native Resource Management)

set -euo pipefail

SA_EMAIL="$1"

# exit early if already initialized
wait_init() {
  kubectl wait --for condition=Initialized pod \
    cnrm-controller-manager-0 -n cnrm-system
}
wait_init && exit 0

# work in a temp directory
CWD="${PWD}"
cd "$(mktemp -d)"

# download and patch Kubernetes config for CNRM
gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
cd "install-bundle-workload-identity"
git apply "${CWD}/0-cnrm-system.yaml.patch"

# apply the config and wait for initialization
kubectl apply -f .
wait_init

# patch the service account
kubectl annotate serviceaccount \
  -n cnrm-system cnrm-controller-manager \
  --overwrite "iam.gke.io/gcp-service-account=${SA_EMAIL}"
