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

variable "max_app_node_count" {
  type        = number
  default     = 5
  description = "Max number of app nodes per zone"
}

variable "max_batch_node_count" {
  type        = number
  default     = 20
  description = "Max number of batch nodes per zone"
}

variable "bastion_image" {
  type        = string
  description = "Container image for the bastion host"
}
