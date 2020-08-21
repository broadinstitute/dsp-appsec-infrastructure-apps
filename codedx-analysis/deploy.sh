#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

PROJECT_NUMBER=$(
    gcloud projects describe "${PROJECT_ID}" --format 'value(projectNumber)'
)
export PROJECT_NUMBER

export NAMESPACE="codedx-analysis"

./kube-apply.py \
    "namespace.yaml" \
    "configconnectorcontext.yaml"

export CODEDX_URL="http://codedx.codedx.svc.cluster.local"
export SECRET_NAME="codedx-api-key"
export SECRET_VERSION="1"
export JOB_DEPLOYMENT="${NAMESPACE}"
export JOB_TOPIC="${NAMESPACE}"
export JOB_SUBSCRIPTION="${JOB_TOPIC}"

export BUCKET_NAME="${PROJECT_ID}-zap-vuln-reports"
export BUCKET_NOTIFICATION="${BUCKET_NAME}-notification"
export BUCKET_IAM_POLICY="${BUCKET_NAME}-iam-policy"
export BUCKET_SA_IAM_POLICY="${BUCKET_NAME}-sa-iam-policy"

export SERVICE="${JOB_DEPLOYMENT}"
export SERVICE_ACCOUNT="${SERVICE}"

export CODEDX_ANALYSIS_SECRET="${NAMESPACE}"

./kube-apply.py "service-account.yaml" \
    "${CWD}/deployment.yaml"
