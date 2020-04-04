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
    ./kubectl.sh apply --filename \
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

kube_install google/knative-gcp \
  cloud-run-events.yaml

wait_component knative-eventing
