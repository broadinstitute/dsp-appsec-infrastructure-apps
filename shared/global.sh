#!/usr/bin/env bash

set -euo pipefail

# Get cluster credentials
gcloud container clusters get-credentials --zone "${zone}" "${cluster}"

# Deploy Config Connector
./cnrm.sh "${cnrm_sa}"

# Create and switch to the namespace for global resources

export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="dsp-appsec"

./namespace.sh

# Deploy global resources using Config Connector:
# - Cloud Armor policy for ingress from Broad IPs
# - DNS Managed Zone
# - Global Static IP

export IP_NAME="${DNS_ZONE}"

./kube-apply.py "global.yaml"

# Wait for the IP to be ready

IP_ADDRESS=$(
  kubectl wait --for condition=Ready computeaddress \
    "${IP_NAME}" -o jsonpath='{.spec.address}'
)
export IP_ADDRESS

# Set/update DNS hostname records
# for each of the services

HOSTS=("defectdojo")
DNS_HOSTNAMES=()

for HOST in "${HOSTS[@]}"; do
  export HOST
  export DNS_HOSTNAME="${HOST}.${DNS_DOMAIN}"
  DNS_HOSTNAMES+=("${DNS_HOSTNAME}")
  ./kube-apply.py "dns.yaml"
done

# Wait for DNS propagation of all

./wait-dns.py "${IP_ADDRESS}" "${DNS_HOSTNAMES[@]}"

# Set up the Ingress and Managed Certificates for all services

export INGRESS="${DNS_ZONE}"

./kube-apply.py "ingress.yaml"
