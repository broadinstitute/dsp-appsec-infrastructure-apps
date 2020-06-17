#!/usr/bin/env bash

set -euo pipefail

export NAMESPACE="zap-report-subscriber"

./kube-apply.py "namespace.yaml"
export CODEDX_URL = "http://codedx.codedx.svc.cluster.local"
export PROJECT_NUMBER="${PROJECT_NUMBER}"
export SECRET_NAME="codedx-api-key"
export SECRET_VERSION="1"
export JOB_TOPIC="zap-scans"
export JOB_SUBSCRIPTION="${JOB_TOPIC}"
export JOB_DEPLOYMENT="${JOB_TOPIC}-dispatcher"
export JOB_CONFIG_VOLUME="job-config"
export JOB_CONFIG_MOUNT_PATH="/job"
export JOB_SPEC_KEY="spec"

export SERVICE="${JOB_DEPLOYMENT}"
export SERVICE_ACCOUNT="${SERVICE}"

./kube-apply.py "service-account.yaml" \
    "${CWD}/deployment.yaml"