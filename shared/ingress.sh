#!/usr/bin/env bash

set -euo pipefail

###
# This script waits for a static IP address to be created,
# sets DNS record for it, waits for DNS propagation,
# and finally deploys GKE Ingress and Service with
# Managed Certificate and Cloud Armor policy.
#
# Inputs:
#   DNS_ZONE, DNS_DOMAIN, BROAD_INGRESS_CSP,
#   NAMESPACE, SERVICE, TARGET_PORT, IP_NAME,
#

# Set/update DNS hostname record

cd "$(dirname "$0")"

IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    "${IP_NAME}" -o jsonpath='{.spec.address}'
)
export IP_ADDRESS
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

./kube-apply.py "dns.yaml"
./wait-dns.py

# Set up Ingress and related resources

export INGRESS="${SERVICE}"
export MANAGED_CERT="${SERVICE}"
export BACKEND_CONFIG="${SERVICE}"
export SERVICE_PORT="http"

./kube-apply.py "ingress.yaml"
