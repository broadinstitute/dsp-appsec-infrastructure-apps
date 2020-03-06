#!/usr/bin/env bash

set -euo pipefail

# Generate secrets

export NAMESPACE="defectdojo"

export ADMIN_SECRET="admin"
export CELERY_SECRET="celery"
export DJANGO_SECRET="django"

pass_gen() {
  LC_CTYPE=C tr -dc "a-z0-9" < /dev/urandom | head -c "$1"
}

create_secret() {
  local name=$1 && shift
  local cmd="kubectl create secret generic ${name} -n ${NAMESPACE}"

  while (( $# )) ; do
    local key=$1 && shift
    local len=$1 && shift
    cmd="${cmd} --from-literal=${key}=$(pass_gen "${len}")"
  done

  ${cmd} || true
}

create_secret "${ADMIN_SECRET}" \
  DD_ADMIN_PASSWORD 32

create_secret "${CELERY_SECRET}" \
  DD_CELERY_BROKER_PASSWORD 32

create_secret "${DJANGO_SECRET}" \
  DD_DATABASE_PASSWORD 32 \
  DD_CREDENTIAL_AES_256_KEY 128 \
  DD_SECRET_KEY 128

# Set shared variables

export PROJECT_ID="$(gcloud config get-value project)"

export MANAGED_CERT="defectdojo"
export IP_NAME="defectdojo"
export BACKEND_CONFIG="defectdojo"
export SERVICE="defectdojo"
export DEPLOYMENT="defectdojo"
export SERVICE_ACCOUNT="defectdojo"

export ADMIN_CONFIG="admin"
export CELERY_CONFIG="celery"
export DJANGO_CONFIG="django"

export DD_DATABASE_USER="defectdojo"
export DD_DATABASE_PORT="5432"

export SQL_INSTANCE="defectdojo"
export SQL_REGION="us-east1"

export LOCALHOST="127.0.0.1"

../kube-apply.py "service.yaml"

# Set/update DNS hostname record

export IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    ${IP_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.address}'
)
../kube-apply.py "dns.yaml"

# Wait for DNS propagation

export DNS_HOSTNAME="defectdojo.${DNS_DOMAIN}"
NAME_SERVER=$(
  gcloud dns managed-zones describe "${DNS_ZONE}" --format 'value(nameServers[0])'
)
until host "${DNS_HOSTNAME}" "${NAME_SERVER}" ; do
  sleep 5
done

# Set up Ingress with Managed Certificate

../kube-apply.py "ingress.yaml"
