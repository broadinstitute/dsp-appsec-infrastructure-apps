#!/usr/bin/env bash

set -euo pipefail

export NAMESPACE="codedx-analysis"

./kube-apply.py "namespace.yaml"
export CODEDX_URL = "http://codedx.codedx.svc.cluster.local"
export SECRET_NAME="codedx-api-key"
export SECRET_VERSION="1"
export JOB_TOPIC="codedx-analysis"
export JOB_SUBSCRIPTION="${JOB_TOPIC}"
export JOB_DEPLOYMENT="${JOB_TOPIC}-dispatcher"
export JOB_CONFIG_VOLUME="job-config"
export JOB_CONFIG_MOUNT_PATH="/job"
export JOB_SPEC_KEY="spec"

export BUCKET_NAME="zap-vulnerability-reports"
export BUCKET_NOTIFICATION="${BUCKET_NAME}-notification"
export BUCKET_ACCESS="${BUCKET_NAME}-access-policy"
export BUCKET_ACCESS_ENTITY="appsec@broadiinstitute.org"

export SERVICE="${JOB_DEPLOYMENT}"
export SERVICE_ACCOUNT="${SERVICE}"

./kube-apply.py "service-account.yaml" \
    "${CWD}/deployment.yaml"