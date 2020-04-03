### Bastion host for cluster access

locals {
  bastion_name = "${var.cluster_name}-bastion"
  bastion_tags = [local.bastion_name]
}

resource "google_project_service" "iap" {
  service = "iap.googleapis.com"
}

resource "google_compute_address" "bastion" {
  name = local.bastion_name
}

resource "google_compute_instance" "bastion" {
  name         = local.bastion_name
  zone         = var.zones[0]
  machine_type = "e2-micro"

  boot_disk {
    initialize_params {
      image = "gce-uefi-images/cos-stable"
    }
  }

  allow_stopping_for_update = true

  network_interface {
    subnetwork = google_compute_subnetwork.gke.self_link
    access_config {
      nat_ip = google_compute_address.bastion.address
    }
  }

  shielded_instance_config {
    enable_secure_boot = true
  }

  metadata = {
    google-logging-enabled    = true
    google-monitoring-enabled = true
    gce-container-declaration = yamlencode({
      spec = {
        containers = [{
          image = var.bastion_image
        }]
      }
    })
  }

  service_account {
    email = module.bastion_host_sa.email
    scopes = [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
    ]
  }

  tags = local.bastion_tags
}

resource "google_compute_firewall" "bastion" {
  name    = "allow-bastion-proxy-from-iap"
  network = google_compute_network.gke.self_link

  target_tags = local.bastion_tags

  source_ranges = [
    "35.235.240.0/20",
  ]

  allow {
    protocol = "tcp"
    ports    = ["8888"]
  }
}

module "bastion_host_sa" {
  source       = "./modules/service-account"
  account_id   = "${local.bastion_name}-host"
  display_name = "Bastion host identity for the ${var.cluster_name} cluster"
  roles = [
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ]
}

resource "google_service_account" "bastion_client" {
  account_id   = "${local.bastion_name}-client"
  display_name = "Bastion host client for the ${var.cluster_name} cluster"
}

resource "google_iap_tunnel_instance_iam_binding" "bastion" {
  instance = google_compute_instance.bastion.name
  role     = "roles/iap.tunnelResourceAccessor"
  members = [
    "serviceAccount:${google_service_account.bastion_client.email}",
  ]
}
