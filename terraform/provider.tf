terraform {
  backend "gcs" {
    prefix = "appsec-apps"
  }

  required_providers {
    google = {
      source  = "google"
      version = ">= 5.38.0, < 6.0"
    }

    google-beta = {
      source  = "google-beta"
      version = ">= 5.38.0, < 6.0"
    }
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