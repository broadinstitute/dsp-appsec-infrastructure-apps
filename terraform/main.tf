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
data "google_client_config" "client" {}

data "http" "cloudbuild-ip" {
  url = "https://ipinfo.io/ip"
}

locals {
  cloudbuild_sa   = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  cloudbuild_cidr = "${data.http.cloudbuild-ip.body}/32"
}

### VPC

resource "google_compute_network" "gke" {
  name                    = var.cluster_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "gke" {
  name                     = var.cluster_name
  network                  = google_compute_network.gke.self_link
  ip_cidr_range            = var.node_cidr
  private_ip_google_access = true

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
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

### NAT

resource "google_compute_address" "nat" {
  name = var.cluster_name
}

resource "google_compute_router" "gke" {
  name    = var.cluster_name
  network = google_compute_network.gke.id
}

resource "google_compute_router_nat" "gke" {
  name                               = var.cluster_name
  router                             = google_compute_router.gke.name
  nat_ips                            = [google_compute_address.nat.self_link]
  nat_ip_allocate_option             = "MANUAL_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ALL"
  }
}

locals {
  nat_cidr = "${google_compute_address.nat.address}/32"
}

### Load balancing

resource "google_compute_ssl_policy" "ssl_policy" {
  name            = var.cluster_name
  profile         = "RESTRICTED"
  min_tls_version = "TLS_1_2"
}

### GKE cluster node Service Account

module "node_sa" {
  source       = "./modules/service-account"
  project      = var.project
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

data "google_compute_default_service_account" "default" {}

resource "google_service_account_iam_member" "compute_sa_cloudbuild" {
  service_account_id = data.google_compute_default_service_account.default.name
  role               = "roles/iam.serviceAccountUser"
  member             = local.cloudbuild_sa
}

### Google Container Registry

resource "google_container_registry" "us_gcr" {
  location = "US"
}

resource "google_storage_bucket_iam_member" "us_gcr_viewers" {
  for_each = {
    node_sa         = "serviceAccount:${module.node_sa.email}"
    bastion_host_sa = "serviceAccount:${module.bastion_host_sa.email}"
  }
  bucket = google_container_registry.us_gcr.id
  role   = "roles/storage.objectViewer"
  member = each.value
}

# needed for CIS GKE 5.1.3

resource "google_container_registry" "gcr" {}

resource "google_storage_bucket_iam_member" "gcr_viewer" {
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

  network         = google_compute_network.gke.self_link
  subnetwork      = google_compute_subnetwork.gke.self_link
  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {}

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_cidr
  }

  dynamic "master_authorized_networks_config" {
    for_each = toset([0])
    content {
      dynamic "cidr_blocks" {
        for_each = toset(concat(
          var.master_autorized_networks,
          [local.cloudbuild_cidr, local.nat_cidr],
        ))
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
    workload_pool = "${var.project}.svc.id.goog"
  }

  network_policy {
    enabled = true
  }

  # pod_security_policy_config {
  #   enabled = true
  # }

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
    google_service_account_iam_member.compute_sa_cloudbuild,
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

  initial_node_count = 2
  machine_type       = "e2-standard-2"
}

# This pool will be used for the application Pods,
# with GKE Sandbox and Cluster Autoscaler enabled

module "apps_node_pool" {
  source = "./modules/node-pool"

  name            = "apps"
  location        = var.region
  cluster         = google_container_cluster.cluster.name
  service_account = module.node_sa.email

  machine_type   = "n1-highmem-4"
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

  machine_type   = "n2-highmem-4"
  min_node_count = 0
  max_node_count = var.max_batch_node_count

  preemptible    = true
  enable_sandbox = true
}

### Config Connector Service Account and Role

module "cnrm_sa" {
  source       = "./modules/service-account"
  project      = var.project
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
    "iam.serviceAccounts.getAccessToken",
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.list",
    "iam.serviceAccounts.create",
    "iam.serviceAccounts.update",
    "iam.serviceAccounts.delete",
    "iam.serviceAccounts.getIamPolicy",
    "iam.serviceAccounts.setIamPolicy",
    "monitoring.metricDescriptors.list",
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
    "storage.buckets.update",
    "storage.buckets.getIamPolicy",
    "storage.buckets.setIamPolicy"
  ]
}

resource "google_service_account_iam_member" "cnrm_sa_ksa_binding" {
  service_account_id = module.cnrm_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project}.svc.id.goog[cnrm-system/cnrm-controller-manager-${var.global_namespace}]"
}

### IAP

data "http" "iap_brand" {
  url = "https://iap.googleapis.com/v1/projects/${var.project}/brands"
  request_headers = {
    Authorization = "Bearer ${data.google_client_config.client.access_token}"
  }
  depends_on = [
    google_project_iam_member.oauth_cloudbuild
  ]
}

resource "google_project_iam_member" "oauth_cloudbuild" {
  project = var.project
  role    = "roles/oauthconfig.editor"
  member  = local.cloudbuild_sa
}

resource "google_iap_client" "iap" {
  display_name = var.cluster_name
  brand        = jsondecode(data.http.iap_brand.body).brands[0].name
}

resource "local_file" "iap_secret" {
  filename        = "${path.cwd}/.iap-secret.yaml"
  file_permission = "0600"
  sensitive_content = yamlencode({
    apiVersion = "v1"
    kind       = "Secret"
    type       = "Opaque"
    metadata = {
      namespace = "$${NAMESPACE}"
      name      = local.iap_secret_name
    }
    data = {
      client_id     = base64encode(google_iap_client.iap.client_id)
      client_secret = base64encode(google_iap_client.iap.secret)
    }
  })
}

locals {
  iap_secret_name = "iap-client"
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

output "ssl_policy" {
  value = google_compute_ssl_policy.ssl_policy.name
}

output "nat_cidr" {
  value = local.nat_cidr
}

output "iap_secret_yaml" {
  value = local_file.iap_secret.filename
}

output "iap_secret_name" {
  value = local.iap_secret_name
}
