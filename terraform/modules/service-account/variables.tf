variable "project" {
  type        = string
  description = "GCP project ID"
}

variable "account_id" {
  type        = string
  description = "Service Account ID"
}

variable "display_name" {
  type        = string
  default     = ""
  description = "Service Account display name"
}

variable "roles" {
  type        = list(string)
  description = "Role name(s), e.g. owner"
}
