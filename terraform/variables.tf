variable "project" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  default     = "us-east1"
  description = "GCP region for deployment"
}

variable "zones" {
  type        = list(string)
  default     = ["us-east1-b", "us-east1-c"]
  description = "GCP zones for GKE cluster"
}

variable "cluster_name" {
  type    = string
  default = "appsec-apps"
}

variable "cluster_nodes_max" {
  type        = number
  default     = 10
  description = "Limit on the cluster size"
}
