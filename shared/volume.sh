#!/usr/bin/env bash

set -euo pipefail

./kube-apply.py "disk.yaml"

# TODO re-enable once this issue is resolved:
# https://github.com/GoogleCloudPlatform/k8s-config-connector/issues/521

# kubectl wait --for condition=Ready ComputeDisk \
#     "${SERVICE_DISK}" -n "${NAMESPACE}" --timeout "180s"

# ./kube-apply.py "volume.yaml"
