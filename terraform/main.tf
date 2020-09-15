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

resource "google_project_service" "firestore" {
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "servicenetworking" {
  service            = "servicenetworking.googleapis.com"
  disable_on_destroy = false
}

data "google_project" "project" {}

locals {
  cloudbuild_sa = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
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


resource "google_compute_global_address" "mysql" {
  name          = "${var.cluster_name}-mysql"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 24
  network       = google_compute_network.gke.id
}

resource "google_compute_global_address" "postgres" {
  name          = "${var.cluster_name}-postgres"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 24
  network       = google_compute_network.gke.id
}

resource "google_service_networking_connection" "sql" {
  network = google_compute_network.gke.id
  service = "servicenetworking.googleapis.com"

  reserved_peering_ranges = [
    google_compute_global_address.mysql.name,
    google_compute_global_address.postgres.name,
  ]

  depends_on = [
    google_project_service.servicenetworking,
  ]
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

resource "google_service_account_iam_member" "node_sa_cloudbuild" {
  service_account_id = module.node_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = local.cloudbuild_sa
}

### Google Container Registry

resource "google_container_registry" "gcr" {
  location = "US"
}

resource "google_storage_bucket_iam_member" "gcr_viewers" {
  for_each = {
    node_sa         = "serviceAccount:${module.node_sa.email}"
    bastion_host_sa = "serviceAccount:${module.bastion_host_sa.email}"
  }
  bucket = google_container_registry.gcr.id
  role   = "roles/storage.objectViewer"
  member = each.value
}

### GKE cluster

resource "google_container_cluster" "cluster" {
  provider = google-beta

  name           = var.cluster_name
  location       = var.region
  node_locations = var.zones

  network         = google_compute_network.gke.self_link
  subnetwork      = google_compute_subnetwork.gke.self_link
  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {}

  dynamic "master_authorized_networks_config" {
    for_each = toset([0])
    content {
      dynamic "cidr_blocks" {
        for_each = toset(var.master_autorized_networks)
        content {
          cidr_block = cidr_blocks.value
        }
      }
    }
  }

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
    config_connector_config {
      enabled = true
    }
    istio_config {
      disabled = true
    }
  }

  depends_on = [
    google_service_account_iam_member.node_sa_cloudbuild,
  ]
}

# This pool will be used for kube-system, Knative and
# Config Connector Pods, in place of the default one
# (such that any changes to it will not require
# re-creation of the cluster)

module "system_node_pool" {
  source = "./modules/node-pool"

  name            = "system"
  location        = var.region
  cluster         = google_container_cluster.cluster.name
  service_account = module.node_sa.email

  initial_node_count = 3
  machine_type       = "e2-small"
}

# This pool will be used for the application Pods,
# with GKE Sandbox and Cluster Autoscaler enabled

module "apps_node_pool" {
  source = "./modules/node-pool"

  name            = "apps"
  location        = var.region
  cluster         = google_container_cluster.cluster.name
  service_account = module.node_sa.email

  machine_type   = "n1-highmem-2"
  max_node_count = var.max_app_node_count
  enable_sandbox = true
}

# This preemptible node pool will be used for batch workloads,
# with GKE Sandbox and Cluster Autoscaler enabled

module "batch_node_pool" {
  source = "./modules/node-pool"

  name            = "batch"
  location        = var.region
  cluster         = google_container_cluster.cluster.name
  service_account = module.node_sa.email

  machine_type   = "n1-highmem-2"
  min_node_count = 0
  max_node_count = var.max_batch_node_count

  preemptible    = true
  enable_sandbox = true
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
    "bigquery.datasets.get",
    "bigquery.datasets.create",
    "bigquery.datasets.update",
    "bigquery.datasets.getIamPolicy",
    "bigquery.datasets.setIamPolicy",
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
    "compute.regionOperations.get",
    "compute.resourcePolicies.get",
    "compute.resourcePolicies.list",
    "compute.resourcePolicies.create",
    "compute.resourcePolicies.use",
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
    "monitoring.timeSeries.create",
    "pubsub.topics.get",
    "pubsub.topics.create",
    "pubsub.topics.attachSubscription",
    "pubsub.topics.update",
    "pubsub.topics.delete",
    "pubsub.topics.getIamPolicy",
    "pubsub.topics.setIamPolicy",
    "pubsub.subscriptions.get",
    "pubsub.subscriptions.create",
    "pubsub.subscriptions.update",
    "pubsub.subscriptions.delete",
    "pubsub.subscriptions.getIamPolicy",
    "pubsub.subscriptions.setIamPolicy",
    "resourcemanager.projects.getIamPolicy",
    "resourcemanager.projects.setIamPolicy",
    "storage.buckets.get",
    "storage.buckets.create",
    "storage.buckets.update"
  ]
}

resource "google_service_account_iam_member" "cnrm_sa_ksa_binding" {
  service_account_id = module.cnrm_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[cnrm-system/cnrm-controller-manager-${var.global_namespace}]"
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

output "sql_network" {
  value = google_service_networking_connection.sql.network
}
