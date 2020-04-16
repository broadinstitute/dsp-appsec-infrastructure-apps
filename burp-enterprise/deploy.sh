#!/usr/bin/env bash

set -euo pipefail

CWD="${PWD}"
cd ../shared

# Create namespace

export NAMESPACE="burp-enterprise"

./kube-apply.py "namespace.yaml"

# Deploy the service

export SERVICE="${NAMESPACE}"

export SERVICE_ACCOUNT="${NAMESPACE}"
export DEPLOYMENT="${SERVICE}"

export LOGBACK_CONFIG="${SERVICE}-logback"
export LOGBACK_CONFIG_VOLUME="${LOGBACK_CONFIG}"
export LOGBACK_CONFIG_PATH="/logback"
export LOGBACK_CONFIG_FILE="logback.xml"
export LOGBACK_LOG_FILE="/var/log/burp.log"

export SECRET_LICENSE="${SERVICE}-license"
export SECRET_LICENSE_VOLUME="${SECRET_LICENSE}"
export SECRET_LICENSE_PATH="/license"
export SECRET_LICENSE_FILE="prefs.xml"

echo "
  Please set up Burp Enterprise license secret with
    kubectl create secret generic ${SECRET_LICENSE} -n ${NAMESPACE} \\
      --from-file <path/to/${SECRET_LICENSE_FILE}> --dry-run -o yaml |
    kubectl apply -f -
"

export SECRET_CONFIG="${SERVICE}"
export SECRET_CONFIG_VOLUME="${SECRET_CONFIG}"
export SECRET_CONFIG_PATH="/config"
export SECRET_CONFIG_FILE="enterprise-server.config"

export DB_SECRET="${SERVICE}-db"
export DB_PORT="5432"
export DB_NAME="burp"
export DB_USER="burpsuite"

./gen-secret.sh "${DB_SECRET}" \
  DB_PASSWORD 32

DB_PASSWORD=$(
  kubectl get secret "${DB_SECRET}" -n "${NAMESPACE}" \
    -o jsonpath='{.data.DB_PASSWORD}' | base64 --decode
)
export DB_PASSWORD

export SQL_INSTANCE="burpsuite-enterprise"
export SQL_REGION="us-east1"

export IP_NAME="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"
export TARGET_PORT="http"

export BURP_VERSION="2020.2"

./kube-apply.py \
  "service-account.yaml" \
  "${CWD}/secret-config.yaml" \
  "${CWD}/deployment.yaml"

./host.sh

./kube-apply.py \
  "ingress.yaml"
