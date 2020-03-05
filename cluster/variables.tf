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

variable "cluster_max_cpu" {
  type        = number
  default     = 16
  description = "vCPU limit for the cluster"
}

variable "cluster_max_mem_gb" {
  type        = number
  default     = 64
  description = "Memory limit for the cluster"
}
