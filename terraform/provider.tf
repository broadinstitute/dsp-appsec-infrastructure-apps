terraform {
  backend "gcs" {
    prefix = "appsec-apps"
  }

  required_providers {
    google = {
      source  = "google"
      version = "> 6.0, <=7.2.0"
    }

    google-beta = {
      source  = "google-beta"
      version = "> 6.0, <=7.2.0"
    }
  }
}

provider "google" {
  add_terraform_attribution_label = false
  project = var.project
  region  = var.region
}

provider "google-beta" {
  project = var.project
  region  = var.region
}