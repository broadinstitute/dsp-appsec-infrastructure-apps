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

variable "cluster_cpu" {
  type = object({
    min = number
    max = number
  })
  default = {
    min = 1
    max = 8
  }
  description = "vCPU limits for the cluster"
}

variable "cluster_mem_gb" {
  type = object({
    min = number
    max = number
  })
  default = {
    min = 2
    max = 32
  }
  description = "Memory limits for the cluster"
}
