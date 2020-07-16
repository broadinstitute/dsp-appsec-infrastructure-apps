#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

export NAMESPACE="codedx-analysis"

./kube-apply.py "namespace.yaml"
export CODEDX_URL = "http://codedx.codedx.svc.cluster.local"
export SECRET_NAME="codedx-api-key"
export SECRET_VERSION="1"
export JOB_DEPLOYMENT="${NAMESPACE}"
export JOB_TOPIC="${NAMESPACE}"
export JOB_SUBSCRIPTION="${JOB_TOPIC}"

export BUCKET_NAME="zap-vulnerability-reports"
export BUCKET_NOTIFICATION="${BUCKET_NAME}-notification"
export BUCKET_IAM_POLICY="${BUCKET_NAME}-iam-policy"
export BUCKET_SA_IAM_POLICY="${BUCKET_NAME}-sa-iam-policy"

export SERVICE="${JOB_DEPLOYMENT}"
export SERVICE_ACCOUNT="${SERVICE}"

export CODEDX_ANALYSIS_SECRET="codedx-anaylsis"

./kube-apply.py "service-account.yaml" \
    "${CWD}/deployment.yaml"
