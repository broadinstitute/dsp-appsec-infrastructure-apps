#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared
export $(xargs < .env)

export NAMESPACE="sdarq"
export DEPLOYMENT="${NAMESPACE}"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export SERVICE_ACCOUNT="${SDARQ_SERVICE_ACCOUNT}"
export SERVICE="${NAMESPACE}"
export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export FRONTEND_CONFIG="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export CRON_JOB="security-controls-cronjob"
export CRON_SERVICE_ACCOUNT="${CRON_JOB}"

export SDARQ_CONFIG="${SERVICE}"
export SDARQ_SECRET="sdarq"
export CIS_JOB_TOPIC="cis-scans"
export ZAP_JOB_TOPIC="zap-scans"
export SC_FIRESTORE_COLLECTION="security-controls"
export CIS_FIRESTORE_COLLECTION="cis-scans"

export FRONTEND_PORT="frontend"
export BACKEND_PORT="backend"

./kube-apply.py \
  "namespace.yaml" \
  "configconnectorcontext.yaml" \
  "service-account.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

export SERVICE="${CRON_JOB}"
export SERVICE_ACCOUNT="${CRON_SERVICE_ACCOUNT}"
./kube-apply.py "service-account.yaml"

./kube-apply.py \
  "${iap_secret_yaml}" \
  "${CWD}/ingress.yaml"
