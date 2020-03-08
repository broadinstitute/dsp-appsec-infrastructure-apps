#!/usr/bin/env bash

set -euo pipefail

# get cluster credentials
gcloud container clusters get-credentials --zone "${zone}" "${cluster}"

# deploy Config Connector
./cnrm.sh "${cnrm_sa}"

# deploy global resources using Config Connector
export PROJECT_ID="$(gcloud config get-value project)"
export NAMESPACE="${GLOBAL_NAMESPACE}"

./namespace.sh
