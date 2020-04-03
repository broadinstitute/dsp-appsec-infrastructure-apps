### Bastion host for cluster access

resource "google_project_service" "iap" {
  service = "iap.googleapis.com"
}

resource "google_compute_address" "bastion" {
  name = "${var.cluster_name}-bastion"
}

resource "google_compute_instance" "bastion" {
  name         = "${var.cluster_name}-bastion"
  zone         = var.zones[0]
  machine_type = "f1-micro"

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
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring.write",
    ]
  }

  tags = local.bastion_tags
}

locals {
  bastion_tags = ["${var.cluster_name}-bastion-proxy"]
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
  account_id   = "${var.cluster_name}-bastion-host"
  display_name = "Bastion host identity for the ${var.cluster_name} cluster"
  roles        = []
}

resource "google_service_account" "bastion_client" {
  account_id   = "${var.cluster_name}-bastion-client"
  display_name = "Bastion host client for the ${var.cluster_name} cluster"
}

resource "google_iap_tunnel_instance_iam_binding" "bastion" {
  instance = google_compute_instance.bastion.self_link
  role     = "roles/iap.tunnelResourceAccessor"
  members = [
    "serviceAccount:${google_service_account.bastion_client.email}",
  ]
}
