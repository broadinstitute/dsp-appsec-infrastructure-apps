#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create and switch to the namespace

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="sdarq"


./namespace.sh

export SDARQ_SECRET="sdarq"

# Deploy the service

export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export LOCALHOST="127.0.0.1"
export TARGET_PORT="http"

./kube-apply.py  "${CWD}/deployment.yaml"
./ingress.sh
