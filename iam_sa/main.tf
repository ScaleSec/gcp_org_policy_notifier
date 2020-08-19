# Creates the IAM permissions for the SA to make org-policy terraform resources in GRC, 
# dev only for now

terraform {
  required_version = ">= 0.12.20"
}

provider "google" {
  version = "~> 3.34"
  project = var.project_id
  region  = var.region
}

# not going to work until TF supports variable indirection or another workaround is found
# locals {
#   bucket_condition  = "(resource.type == \"storage.googleapis.com/Bucket\" && resource.name.startsWith(\"projects/_/buckets/${var.bucket_name}\")) || (resource.type == \"storage.googleapis.com/Object\" && resource.name.startsWith(\"projects/_/buckets/${var.bucket_name}/objects/${var.folder_path}/${var.environment}/\"))"
# }


# give the SA bindings + conditions
# resource "google_project_iam_member" "bindings_conditions" {
#   for_each = var.conditions_permissions_map

#   project = var.project_id
#   role    = lookup(each.value, "role", "")

#   member = "serviceAccount:${var.service_account_email}"

#   condition {
#     title       = lookup(each.value, "condition_title", "")
#     description = "Access to ${var.environment} only"
#     expression  = lookup(each.value, "condition_exp", "")
#   }
# }

# Bindings without conditions
resource "google_project_iam_member" "bindings_no_conditions" {
  for_each = var.permissions_map

  project = var.project_id
  role    = lookup(each.value, "role", "")

  member = "serviceAccount:${var.service_account_email}"
}

resource "google_organization_iam_custom_role" "org_policy_terraform_custom_role" {
  role_id     = "org_policy_terraform_cfn_${var.environment}"
  org_id      = var.org_id
  title       = "Organization Policy Terraform Role"
  description = "IAM role for Cloud Function to terraform Org Policies"
  permissions = var.custom_role_perms
}

resource "google_organization_iam_member" "org_policy_terraform_member" {
  org_id = var.org_id
  role   = "organizations/${var.org_id}/roles/${google_organization_iam_custom_role.org_policy_terraform_custom_role.role_id}"
  member = "serviceAccount:${var.service_account_email}"
}

