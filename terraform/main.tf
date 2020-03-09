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
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
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

  name           = var.cluster_name
  location       = var.region
  node_locations = var.zones

  network    = google_compute_network.gke.self_link
  subnetwork = google_compute_subnetwork.gke.self_link
  ip_allocation_policy {}

  initial_node_count = 1

  node_config {
    machine_type = "e2-small"
    preemptible  = true

    service_account = module.node_sa.email
    oauth_scopes    = local.oauth_scopes

    image_type = "COS_CONTAINERD"

    shielded_instance_config {
      enable_secure_boot = true
    }
  }

  enable_shielded_nodes = true

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

  network_policy {
    enabled = true
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
  }
}

resource "google_container_node_pool" "cnrm_pool" {
  provider = google-beta

  name     = "cnrm-system"
  location = var.region
  cluster  = google_container_cluster.cluster.name

  node_count = 1

  node_config {
    machine_type = "e2-small"
    preemptible  = true

    service_account = module.node_sa.email
    oauth_scopes    = local.oauth_scopes

    image_type = "COS_CONTAINERD"

    shielded_instance_config {
      enable_secure_boot = true
    }

    labels = {
      "cnrm.cloud.google.com/system" = "true",
    }

    taint = [{
      key    = "cnrm.cloud.google.com/system"
      value  = "true"
      effect = "NO_SCHEDULE"
    }]
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
  roles = [
    google_project_iam_custom_role.cnrm_sa.id,
  ]
}

resource "google_project_iam_custom_role" "cnrm_sa" {
  role_id     = replace("cnrm-system-${var.cluster_name}", "-", "_")
  title       = "AppSec Apps Config Connector"
  description = "Grants access to manage GCP resources via GKE Config Connector in ${var.cluster_name} cluster"
  permissions = [
    "cloudsql.instances.get",
    "cloudsql.instances.list",
    "cloudsql.instances.create",
    "cloudsql.instances.update",
    "cloudsql.users.list",
    "cloudsql.users.update",
    "compute.globalAddresses.get",
    "compute.globalAddresses.create",
    "compute.globalAddresses.setLabels",
    "compute.globalAddresses.delete",
    "compute.securityPolicies.get",
    "compute.securityPolicies.create",
    "compute.securityPolicies.update",
    "compute.securityPolicies.delete",
    "dns.changes.get",
    "dns.changes.create",
    "dns.managedZones.get",
    "dns.managedZones.create",
    "dns.managedZones.update",
    "dns.resourceRecordSets.list",
    "dns.resourceRecordSets.create",
    "dns.resourceRecordSets.update",
    "dns.resourceRecordSets.delete",
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.list",
    "iam.serviceAccounts.create",
    "iam.serviceAccounts.update",
    "iam.serviceAccounts.delete",
    "iam.serviceAccounts.getIamPolicy",
    "iam.serviceAccounts.setIamPolicy",
    "resourcemanager.projects.getIamPolicy",
    "resourcemanager.projects.setIamPolicy",
  ]
}

resource "google_service_account_iam_member" "cnrm_sa_ksa_binding" {
  service_account_id = module.cnrm_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[cnrm-system/cnrm-controller-manager]"
}

### Outputs

output "region" {
  value = var.region
}

output "cluster" {
  value = google_container_cluster.cluster.name
}

output "cnrm_sa" {
  value = module.cnrm_sa.email
}
