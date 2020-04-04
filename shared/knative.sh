#!/usr/bin/env bash

set -euo pipefail

###
# Set up Knative in accordance with
# https://knative.dev/docs/install/any-kubernetes-cluster
#

VERSION="v0.13.0"

kube_install() {
  local repo="$1" && shift

  while (( $# )) ; do
    local res="$1" && shift
    ./kubectl.sh apply -f \
      "https://github.com/${repo}/releases/download/${VERSION}/${res}.yaml"
  done
}

wait_component() {
  ./kubectl.sh wait --for condition=Ready \
    pod -n "$1" --all --timeout 5m
}

# Install Serving component

kube_install knative/serving \
  serving-crds \
  serving-core \
  serving-istio

wait_component knative-serving

# Install Eventing component

kube_install knative/eventing \
  eventing-crds \
  eventing-core

wait_component knative-eventing

# Install GCP Sources with Workload Identity

export NAMESPACE="cloud-run-events"

kube_install google/knative-gcp \
  "${NAMESPACE}".yaml

export IAM_SERVICE_ACCOUNT="${NAMESPACE}-appsec-apps"
export K8S_SERVICE_ACCOUNT="controller"

./kube-apply.py "gcp-events-sa.yaml"

./kubectl.sh annotate serviceaccount "${K8S_SERVICE_ACCOUNT}" -n "${NAMESPACE}" \
  "iam.gke.io/gcp-service-account=${IAM_SERVICE_ACCOUNT}@$PROJECT_ID.iam.gserviceaccount.com"

wait_component "${NAMESPACE}"
