#!/usr/bin/env bash

# Install Config Connector (Cloud Native Resource Management)

set -euo pipefail

SA_EMAIL="$1"
CWD="${PWD}"

# exit early if already initialized
wait_init() {
  "${CWD}/kubectl.sh" wait --for condition=Available deployment \
    cnrm-webhook-manager -n cnrm-system
}
wait_init && exit 0

# work in a temp directory
cd "$(mktemp -d)"

# download CNRM configs
gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
cd "install-bundle-workload-identity"

# apply the configs and wait for initialization
"${CWD}/kubectl.sh" apply -f .
wait_init

# patch the service account
"${CWD}/kubectl.sh" annotate serviceaccount \
  -n cnrm-system cnrm-controller-manager \
  --overwrite "iam.gke.io/gcp-service-account=${SA_EMAIL}"
