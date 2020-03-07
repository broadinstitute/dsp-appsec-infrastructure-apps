#!/usr/bin/env bash

set -euo pipefail

###
# This script waits for a static IP address to be created,
# sets DNS record for it, waits for DNS propagation,
# and finally deploys GKE Ingress and Service with
# Managed Certificate, Cloud Armor policy,
# and Vertical Port Autoscaling.
#
# Inputs:
#   DNS_ZONE, DNS_DOMAIN, BROAD_INGRESS_CSP,
#   NAMESPACE, DEPLOYMENT, TARGET_PORT, IP_NAME,
#

# Set/update DNS hostname record

CWD=$(dirname "$0")

IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    "${IP_NAME}" -o jsonpath='{.spec.address}'
)
export IP_ADDRESS
export DNS_HOSTNAME="${NAMESPACE}.${DNS_DOMAIN}"

${CWD}/kube-apply.py "dns.yaml"
${CWD}/wait-dns.py

# Set up Ingress and related resources

export INGRESS="${DEPLOYMENT}"
export MANAGED_CERT="${DEPLOYMENT}"
export BACKEND_CONFIG="${DEPLOYMENT}"
export SERVICE="${DEPLOYMENT}"
export SERVICE_PORT="http"

${CWD}/kube-apply.py "ingress.yaml"
