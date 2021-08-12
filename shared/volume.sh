#!/usr/bin/env bash

set -euo pipefail

./kube-apply.py "disk.yaml"

kubectl wait --for condition=Ready ComputeDisk \
    "${SERVICE_DISK}" -n "${NAMESPACE}" --timeout "120s"

./kube-apply.py "volume.yaml"
