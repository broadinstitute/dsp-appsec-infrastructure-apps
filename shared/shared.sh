#!/usr/bin/env bash

set -euo pipefail

# get cluster credentials
gcloud container clusters get-credentials --zone "${zone}" "${cluster}"

# deploy Config Connector
./cnrm.sh "${cnrm_sa}"

# deploy shared resources using Config Connector
./kube-apply.py "shared.yaml"
