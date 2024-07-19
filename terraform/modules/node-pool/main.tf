resource "google_container_node_pool" "pool" {
  provider = google-beta

  name     = var.name
  location = var.location
  cluster  = var.cluster

  initial_node_count = var.initial_node_count

  dynamic "autoscaling" {
    for_each = var.min_node_count == var.max_node_count ? [] : [1]
    content {
      min_node_count = var.min_node_count
      max_node_count = var.max_node_count
    }
  }

  dynamic "node_config" {
    for_each = [1]
    content {
      image_type = "COS_CONTAINERD"

      machine_type = var.machine_type
      preemptible  = var.preemptible

      service_account = var.service_account
      oauth_scopes = [
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/monitoring",
      ]

      dynamic "sandbox_config" {
        for_each = var.enable_sandbox ? [1] : []
        content {
          sandbox_type = "gvisor"
        }
      }

      dynamic "taint" {
        for_each = var.enable_sandbox ? [1] : []

        content {
          key    = "sandbox.gke.io/runtime"
          value  = "gvisor"
          effect = "NO_SCHEDULE"
        }
      }

      shielded_instance_config {
        enable_secure_boot = true
      }

      workload_metadata_config {
        mode = "GKE_METADATA"
      }
    }
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }

  timeouts {
    create = "120m"
  }
}
