terraform {
  backend "gcs" {
    prefix = "appsec-apps"
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

### VPC

resource "google_compute_network" "gke" {
  name                    = var.cluster_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gke" {
  name          = var.cluster_name
  network       = google_compute_network.gke.self_link
  ip_cidr_range = "10.2.0.0/16"
}

### Node SA

module "node_sa" {
  source       = "./modules/service-account"
  account_id   = "gke-node-${var.cluster_name}"
  display_name = "GKE node identity for ${var.cluster_name} cluster"
  roles = [
    "logging.logWriter",
    "monitoring.metricWriter",
    "monitoring.viewer",
  ]
}

### GCR

resource "google_container_registry" "gcr" {
  location = "US"
}

resource "google_storage_bucket_iam_member" "node_sa_gcr_role" {
  bucket = google_container_registry.gcr.id
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.node_sa.email}"
}

### Cluster

resource "google_container_cluster" "cluster" {
  provider = google-beta

  name     = var.cluster_name
  location = var.zone

  network    = google_compute_network.gke.self_link
  subnetwork = google_compute_subnetwork.gke.self_link
  ip_allocation_policy {}

  remove_default_node_pool = true
  initial_node_count       = 1

  cluster_autoscaling {
    enabled = true
    resource_limits {
      resource_type = "cpu"
      maximum       = var.cluster_cpu_max
    }
    resource_limits {
      resource_type = "memory"
      maximum       = var.cluster_mem_gb_max
    }
    auto_provisioning_defaults {
      service_account = module.node_sa.email
      oauth_scopes    = local.oauth_scopes
    }
  }

  vertical_pod_autoscaling {
    enabled = true
  }

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    identity_namespace = "${var.project}.svc.id.goog"
  }
}

resource "google_container_node_pool" "node_pool" {
  name       = "primary-pool"
  location   = var.zone
  cluster    = google_container_cluster.cluster.name
  node_count = 1

  node_config {
    service_account = module.node_sa.email
    oauth_scopes    = local.oauth_scopes
  }
}

locals {
  oauth_scopes = [
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
  ]
}

### Config Connector

module "cnrm_sa" {
  source       = "./modules/service-account"
  account_id   = "cnrm-system-${var.cluster_name}"
  display_name = "GKE Config Connector identity for ${var.cluster_name} cluster"
  roles        = [
    "compute.orgSecurityPolicyAdmin",
  ]
}

resource "google_service_account_iam_member" "cnrm_sa_ksa_role" {
  service_account_id = module.cnrm_sa.name
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
  value = module.cnrm_sa.email
}
