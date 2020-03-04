#!/usr/bin/env sh

### Create GKE cluster with Workflow Identity and Config Connector

export PROJECT_ID="$(gcloud config get-value project)"
export ZONE="$(gcloud config get-value compute/zone)"
export NETWORK="defectdojo"
export CLUSTER_NAME="defectdojo"
export CLUSTER_NODES="1"
export CLUSTER_MACHINE_TYPE="n1-standard-2"
export CONFIG_CONNECTOR_SA="cnrm-system-dojo"
export CONFIG_CONNECTOR_SA_EMAIL="${CONFIG_CONNECTOR_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud services enable \
  cloudresourcemanager.googleapis.com \
  sqladmin.googleapis.com

gcloud compute networks create "${NETWORK}"

gcloud beta container clusters create "${CLUSTER_NAME}" \
  --identity-namespace="${PROJECT_ID}.svc.id.goog" \
  --zone "${ZONE}" \
  --network "${NETWORK}" \
  --num-nodes "${CLUSTER_NODES}" \
  --machine-type "${CLUSTER_MACHINE_TYPE}" \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-ip-alias

gcloud iam service-accounts create "${CONFIG_CONNECTOR_SA}"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CONFIG_CONNECTOR_SA_EMAIL}" \
  --role="roles/owner"

gcloud iam service-accounts add-iam-policy-binding "${CONFIG_CONNECTOR_SA_EMAIL}" \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[cnrm-system/cnrm-controller-manager]" \
  --role="roles/iam.workloadIdentityUser"

gcloud container clusters get-credentials "${CLUSTER_NAME}"

(
  cd "$(mktemp -d)" || exit 1
  gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
  cd "install-bundle-workload-identity" || exit 1
  sed -i.bak "s/(gcp-service-account: ).*/\1${CONFIG_CONNECTOR_SA_EMAIL}/" "0-cnrm-system.yaml"
  kubectl apply -f .
)

kubectl annotate namespace default \
  "cnrm.cloud.google.com/project-id=${PROJECT_ID}"
