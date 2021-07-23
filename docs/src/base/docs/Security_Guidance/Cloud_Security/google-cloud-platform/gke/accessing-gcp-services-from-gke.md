---
description: Use Workload Identity
---

# Accessing GCP Services from GKE

**Prerequisites:**

1. A Google Cloud Project
2. `gcloud`  installed and configured

**Note:** You can use an existing cluster, namespace, or Google Service Account instead of creating new ones.

### 1. Enable Workload Identity on a New or Existing Clusters

Option 1: Create a new cluster with workload identity enabled

```bash
gcloud beta container clusters create $CLUSTER_NAME \
  --release-channel regular \
  --workload-pool=$YOUR_PROJECT_ID.svc.id.goog
```

Option 2: Enable workload identity on an existing cluster

```bash
gcloud container clusters update $CLUSTER_NAME \
  --workload-pool=$YOUR_PROJECT_ID.svc.id.goog
```

### 2. Create a Kubernetes Namespace

```bash
kubectl create namespace $NAMESPACE
```

### 3. Create a Google Services Account

```bash
gcloud iam service-accounts create $GSA_NAME
```

### 4. Create the Kubernetes Service Account

```bash
kubectl create serviceaccount --namespace $NAMESPACE $KSA_NAME
```

### 5. Create the IAM Policy Bindings

```bash
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${YOUR_PROJECT_ID}.svc.id.goog[${NAMESPACE}/${KSA_NAME}]" \
  $GSA_NAME@$YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 6. Annotate the Kubernetes Service Account

```bash
kubectl annotate serviceaccount \
  --namespace $NAMESPACE \
  $KSA_NAME \
  iam.gke.io/gcp-service-account=$GSA_NAME@$YOUR_PROJECT_ID.iam.gserviceaccount.com
```

In order to access services, you then need to grant permissions to your google service account using Google IAM. You can verify if you configured the service accounts correctly by creating a pod and launching it interactively(see below).

```bash
kubectl run -it \
  --generator=run-pod/v1 \
  --image google/cloud-sdk:slim \
  --serviceaccount $KSA_NAME \
  --namespace $NAMESPACE \
  workload-identity-test
```

You can then run `google auth list` inside the pod to see the Google Service Account.

