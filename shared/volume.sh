#!/usr/bin/env bash

set -euo pipefail

export COMPUTE_DISK=${NAMESPACE}

./kube-apply.sh "disk.yaml"

kubectl wait --for condition=Ready ComputeDisk \
    "${COMPUTE_DISK}" -n "${NAMESPACE}"

./kube-apply.sh "volume.yaml"
