#!/usr/bin/env bash

set -eu

./kube-apply.py "namespace.yaml"
kubectl config set-context --current --namespace "${NAMESPACE}"
