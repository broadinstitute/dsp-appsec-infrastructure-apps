variable "project" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  default     = "us-east1"
  description = "GCP region for deployment"
}

variable "zone" {
  type        = string
  default     = "us-east1-b"
  description = "GCP zone for GKE cluster"
}

variable "cluster_name" {
  type    = string
  default = "appsec-apps"
}

variable "cluster_cpu_max" {
  type        = number
  default     = 8
  description = "vCPU limit for the cluster"
}

variable "cluster_mem_gb_max" {
  type        = number
  default     = 32
  description = "Memory limit for the cluster"
}
