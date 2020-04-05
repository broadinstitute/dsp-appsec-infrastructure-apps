variable "name" {
  type        = string
  description = "Node pool name"
}

variable "cluster" {
  type        = string
  description = "Cluster name"
}

variable "location" {
  type        = string
  description = "Cluster region/zone"
}

variable "initial_node_count" {
  type        = number
  default     = 0
  description = "Initial node count"
}

variable "min_node_count" {
  type        = number
  default     = 1
  description = "Minimum number of nodes (per zone, for a regional cluster)"
}

variable "max_node_count" {
  type        = number
  default     = 1
  description = "Maximum number of nodes (per zone, for a regional cluster)"
}

variable "machine_type" {
  type        = string
  default     = "n1-standard-1"
  description = "GCE node type"
}

variable "preemptible" {
  type        = bool
  default     = false
  description = "Use preemptible instances"
}

variable "service_account" {
  type        = string
  description = "Node Service Account email"
}

variable "enable_sandbox" {
  type        = bool
  default     = false
  description = "Enable GKE Sandbox"
}
