#!/usr/bin/env bash

set -euo pipefail

###
# This script waits for a static IP address to be created,
# sets DNS record for it, waits for DNS propagation,
# and finally deploys GKE Ingress and Managed Certificate for it.
#
# Inputs: NAMESPACE, DNS_ZONE, DNS_DOMAIN, SERVICE, IP_NAME env variables.
#

# Set/update DNS hostname record

CWD=$(dirname "$0")

export DNS_HOSTNAME="${SERVICE}.${DNS_DOMAIN}"
export IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    "${IP_NAME}" -n "${NAMESPACE}" -o jsonpath='{.spec.address}'
)

${CWD}/kube-apply.py "dns.yaml"

# Wait for DNS propagation

NAME_SERVER=$(
  gcloud dns managed-zones describe "${DNS_ZONE}" --format 'value(nameServers[0])'
)
until host "${DNS_HOSTNAME}" "${NAME_SERVER}" ; do
  sleep 5
done

# Set up Ingress with Managed Certificate

export MANAGED_CERT="${NAMESPACE}-cert"

${CWD}/kube-apply.py "ingress.yaml"
