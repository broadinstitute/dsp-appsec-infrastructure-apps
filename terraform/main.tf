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

### GKE cluster node Service Account

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

### Google Container Registry

resource "google_container_registry" "gcr" {
  location = "US"
}

resource "google_storage_bucket_iam_member" "node_sa_gcr_role" {
  bucket = google_container_registry.gcr.id
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.node_sa.email}"
}

### GKE cluster

resource "google_container_cluster" "cluster" {
  provider = google-beta

  name           = var.cluster_name
  location       = var.region
  node_locations = var.zones

  network    = google_compute_network.gke.self_link
  subnetwork = google_compute_subnetwork.gke.self_link
  ip_allocation_policy {}

  initial_node_count       = 1
  remove_default_node_pool = true
  enable_shielded_nodes    = true

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

# This pool will be used for kube-system and
# Config Connector Pods, in place of the default one
# (such that any changes to it will not require
# re-creation of the cluster)

resource "google_container_node_pool" "system" {
  provider = google-beta

  name     = "system"
  location = var.region
  cluster  = google_container_cluster.cluster.name

  initial_node_count = 1

  node_config {
    machine_type = "e2-small"

    service_account = module.node_sa.email
    oauth_scopes    = local.oauth_scopes

    image_type = "COS_CONTAINERD"

    shielded_instance_config {
      enable_secure_boot = true
    }

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }
}

# This pool will be used for the application Pods,
# with GKE Sandbox and Cluster Autoscaler enabled

resource "google_container_node_pool" "sandbox" {
  provider = google-beta

  name     = "sandbox"
  location = var.region
  cluster  = google_container_cluster.cluster.name

  autoscaling {
    min_node_count = 1
    max_node_count = var.zone_max_node_count - 1
  }

  node_config {
    service_account = module.node_sa.email
    oauth_scopes    = local.oauth_scopes

    image_type = "COS_CONTAINERD"

    sandbox_config {
      sandbox_type = "gvisor"
    }

    shielded_instance_config {
      enable_secure_boot = true
    }

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }

  timeouts {
    create = "60m"
  }
}

locals {
  oauth_scopes = [
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
  ]
}

### Config Connector Service Account and Role

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
    "cloudsql.databases.get",
    "cloudsql.databases.list",
    "cloudsql.databases.create",
    "cloudsql.databases.update",
    "cloudsql.users.list",
    "cloudsql.users.create",
    "cloudsql.users.update",
    "compute.disks.get",
    "compute.disks.list",
    "compute.disks.create",
    "compute.disks.setLabels",
    "compute.disks.update",
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
    "compute.resourcePolicies.get",
    "compute.resourcePolicies.list",
    "compute.resourcePolicies.create",
    "compute.resourcePolicies.use",
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
