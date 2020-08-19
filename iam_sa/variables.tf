variable "environment" {
  description = "dev|prod"
}

variable "bucket_name" {
  description = "bucket name"
}

variable "folder_path" {
  description = "folder name in the bucket"
}

variable "service_account_email" {
  description = "email of service account"
}

variable "project_id" {
  type        = string
  description = "The ID of the project where the resources will be created."
}

variable "region" {
  type        = string
  description = "The region in which resources will be applied."
  default     = "us-central1"
}

variable "permissions_map" {
  description = "Maps roles to binding"
  type = map(any)
}

variable "conditions_permissions_map" {
  description = "Maps roles to conditions"
  type = map(any)
}

variable "org_id" {
  description = "The GCP Org ID to assign permissions to."
}

variable "custom_role_perms" {
  type = list(string)
  description = "List of permissions to grant at an org level for the custom role"
  default     = []
}
