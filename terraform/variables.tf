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
  default     = 10
  description = "Max number of app nodes per zone"
}

variable "max_batch_node_count" {
  type        = number
  default     = 20
  description = "Max number of batch nodes per zone"
}

variable "master_autorized_networks" {
  type = list(string)
  default = [
    "69.173.64.0/19",
    "69.173.96.0/20",
    "69.173.112.0/21",
    "69.173.120.0/22",
    "69.173.124.0/23",
    "69.173.126.0/24",
    "69.173.127.0/25",
    "69.173.127.128/26",
    "69.173.127.192/27",
    "69.173.127.224/30",
    "69.173.127.228/32",
    "69.173.127.230/31",
    "69.173.127.232/29",
    "69.173.127.240/28",
  ]
  description = "Networks allowed to access GKE master"
}

variable "master_cidr" {
  type        = string
  default     = "172.16.0.32/28"
  description = "CIDR for the cluster master"
}
variable "node_cidr" {
  type        = string
  default     = "10.2.0.0/16"
  description = "CIDR for the cluster nodes"
}

variable "global_namespace" {
  type        = string
  description = "Global namespace for GKE"
}

variable "bastion_image" {
  type        = string
  description = "Docker image name for bastion proxy"
}

variable "bastion_port" {
  type        = number
  description = "Port for bastion proxy"
}
