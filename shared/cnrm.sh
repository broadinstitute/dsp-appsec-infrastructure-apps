#!/usr/bin/env bash

# Install Config Connector (Cloud Native Resource Management)

set -euo pipefail

SA_EMAIL="$1"

# exit early if already initialized
wait_init() {
  kubectl wait --for condition=Available deployment \
    cnrm-webhook-manager -n cnrm-system
}
wait_init && exit 0

# work in a temp directory
cd "$(mktemp -d)"

# download CNRM configs
# use fixed release until they fix it...
gsutil cat "gs://cnrm/1.14.0/release-bundle.tar.gz" | tar xzf -
cd "install-bundle-workload-identity"

# apply the configs and wait for initialization
kubectl apply -f .
wait_init

# patch the service account
kubectl annotate serviceaccount \
  -n cnrm-system cnrm-controller-manager \
  --overwrite "iam.gke.io/gcp-service-account=${SA_EMAIL}"
