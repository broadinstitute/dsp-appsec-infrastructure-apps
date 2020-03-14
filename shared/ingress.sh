#!/usr/bin/env bash

set -euo pipefail

###
# This script:
# - creates a static IP for the service,
# - waits for it to be created,
# - sets DNS record for it
# - waits for DNS propagation,
# - deploys GKE Ingress and Service with
#   Managed Certificate and Cloud Armor policy.
#
# Inputs:
#   DNS_ZONE, DNS_DOMAIN, BROAD_INGRESS_CSP,
#   NAMESPACE, SERVICE, TARGET_PORT
#

# Create the IP

cd "$(dirname "$0")"

export IP_NAME="${NAMESPACE}"
./kube-apply.py "ip.yaml"

# Wait for IP creation

IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    "${IP_NAME}" -n "${NAMESPACE}" \
    -o jsonpath='{.spec.address}'
)

# Set/update DNS hostname record

export IP_ADDRESS
export DNS_RECORD="${NAMESPACE}"
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

./kube-apply.py "dns.yaml"
./wait-dns.py

# Set up Ingress and related resources

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"

./kube-apply.py "ingress.yaml"
