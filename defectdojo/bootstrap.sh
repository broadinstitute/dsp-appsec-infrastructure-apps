#!/usr/bin/env sh

### Create GKE cluster with Workflow Identity and Config Connector

export PROJECT_ID="$(gcloud config get-value project)"
export ZONE="$(gcloud config get-value compute/zone)"
export NETWORK="defectdojo"
export CLUSTER_NAME="defectdojo"
export CLUSTER_NODES="1"
export CLUSTER_DISK_SIZE="25GB"
export CONFIG_CONNECTOR_SA="cnrm-system-dojo"
export CONFIG_CONNECTOR_SA_EMAIL="${CONFIG_CONNECTOR_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud compute networks create "${NETWORK}"

gcloud beta container clusters create "${CLUSTER_NAME}" \
  --identity-namespace="${PROJECT_ID}.svc.id.goog" \
  --zone "${ZONE}" \
  --network "${NETWORK}" \
  --num-nodes "${CLUSTER_NODES}" \
  --disk-size "${CLUSTER_DISK_SIZE}" \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-ip-alias

gcloud iam service-accounts create "${CONFIG_CONNECTOR_SA}"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CONFIG_CONNECTOR_SA_EMAIL}" \
  --role="roles/editor"

gcloud iam service-accounts add-iam-policy-binding "${CONFIG_CONNECTOR_SA_EMAIL}" \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[cnrm-system/cnrm-controller-manager]" \
  --role="roles/iam.workloadIdentityUser"

gcloud container clusters get-credentials "${CLUSTER_NAME}"

(
  cd "$(mktemp -d)" || exit 1
  gsutil cat "gs://cnrm/latest/release-bundle.tar.gz" | tar xzf -
  cd "install-bundle-workload-identity" || exit 1
  sed -i.bak "s/\${PROJECT_ID?}/${PROJECT_ID}/" "0-cnrm-system.yaml"
  kubectl apply -f .
)

### Create configs/secrets for Dojo deployment

pass_gen() {
  LC_CTYPE=C tr -dc "a-zA-Z0-9" < /dev/urandom | head -c "$1"
}

export DNS_HOSTNAME="defectdojo.dsp-appsec.broadinstitute.org"

export DD_DATABASE_USER="dojo"
export DD_DATABASE_PASSWORD=$(pass_gen 32)

export DD_CELERY_BROKER_USER="celery"
export DD_CELERY_BROKER_PASSWORD=$(pass_gen 128)

export DD_SECRET_KEY=$(pass_gen 128)
export DD_CREDENTIAL_AES_256_KEY=$(pass_gen 128)

export DD_ADMIN_FIRST_NAME="AppSec"
export DD_ADMIN_LAST_NAME="Team"
export DD_ADMIN_MAIL="appsec@broadinstitute.org"
export DD_ADMIN_USER="appsec"

brew link --force gettext || brew install gettext || true
envsubst < "bootstrap.yaml" | kubectl apply -f -
