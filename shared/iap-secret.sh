#!/usr/bin/env bash

set -euo pipefail

kubectl get secret "${iap_secret}" -n "${GLOBAL_NAMESPACE}" --export -o json | \
    grep -Ev '(creationTimestamp|resourceVersion|selfLink|uid)' | \
    kubectl apply -n "${NAMESPACE}" -f -
