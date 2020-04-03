#!/usr/bin/env bash

set -euo pipefail

###
# This script:
# - creates a static IP for the service
# - waits for it to be created
# - sets DNS hostname record
# - waits for DNS propagation
# - deploys GKE Managed Certificate for the hostname
#
# Inputs:
#   DNS_ZONE, DNS_HOSTNAME, IP_NAME,
#   NAMESPACE, MANAGED_CERT, BROAD_INGRESS_CSP
#

# Create the IP

cd "$(dirname "$0")"

./kube-apply.py "ip.yaml"

# Wait for IP creation

IP_ADDRESS=$(
  ./kubectl.sh wait --for condition=Ready computeaddress \
    "${IP_NAME}" -n "${NAMESPACE}" \
    -o jsonpath='{.spec.address}'
)

# Set/update DNS hostname record

export IP_ADDRESS
export DNS_RECORD="${NAMESPACE}"

./kube-apply.py "dns.yaml"
./wait-dns.py

# Set up GKE Managed Certificate

./kube-apply.py "cert.yaml"
