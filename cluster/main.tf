terraform {
  backend "gcs" {
    prefix = "gke-appsec"
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

provider "google-beta" {
  project = var.project
  region  = var.region
}

locals {
  cluster_sa = "serviceAccount:${google_service_account.cluster_sa.email}"
}

data "google_client_config" "current" {}

### VPC

resource "google_compute_network" "gke" {
  name                    = "gke-appsec"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gke" {
  name          = "gke-appsec"
  network       = google_compute_network.gke.self_link
  ip_cidr_range = "10.2.0.0/16"
}

### Cluster SA

resource "google_service_account" "cluster_sa" {
  account_id   = "gke-appsec-cluster"
  display_name = "AppSec GKE Cluster identity"
}

resource "google_project_iam_member" "cluster_sa_log_writer_role" {
  role   = "roles/logging.logWriter"
  member = local.cluster_sa
}

resource "google_project_iam_member" "cluster_sa_metric_writer_role" {
  role   = "roles/monitoring.metricWriter"
  member = local.cluster_sa
}

resource "google_project_iam_member" "cluster_sa_monitoring_viewer_role" {
  role   = "roles/monitoring.viewer"
  member = local.cluster_sa
}

### GCR

resource "google_container_registry" "gcr" {
  location = "US"
}

resource "google_storage_bucket_iam_member" "cluster_sa_gcr_role" {
  bucket = google_container_registry.gcr.id
  role   = "roles/storage.objectViewer"
  member = local.cluster_sa
}

### Cluster

resource "google_container_cluster" "cluster" {
  provider = google-beta

  name     = "appsec"
  location = var.zone

  network    = google_compute_network.gke.self_link
  subnetwork = google_compute_subnetwork.gke.self_link
  ip_allocation_policy {}

  remove_default_node_pool = true
  initial_node_count = 1

  cluster_autoscaling {
    enabled = true
    resource_limits {
      resource_type = "cpu"
      maximum       = var.cluster_max_cpu
    }
    resource_limits {
      resource_type = "memory"
      maximum       = var.cluster_max_mem_gb
    }
    auto_provisioning_defaults {
      service_account = google_service_account.cluster_sa.email
    }
  }

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    identity_namespace = "${var.project}.svc.id.goog"
  }
}

### Config Connector

resource "google_service_account" "cnrm_sa" {
  account_id   = "cnrm-system"
  display_name = "AppSec GKE Config Connector identity"
}

resource "google_project_iam_member" "cnrm_sa_owner_role" {
  role   = "roles/owner"
  member = "serviceAccount:${google_service_account.cnrm_sa.email}"
}

resource "google_service_account_iam_member" "cnrm_sa_ksa_role" {
  service_account_id = google_service_account.cnrm_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[cnrm-system/cnrm-controller-manager]"
}

### Outputs

output "zone" {
  value = var.zone
}

output "cluster" {
  value = google_container_cluster.cluster.name
}

output "cnrm_sa" {
  value = google_service_account.cnrm_sa.email
}
