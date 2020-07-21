terraform {
  required_version = ">= 0.12"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  version = "~> 2.5"
  project = var.project_id
  region  = var.region
}

#------------------------#
# GCS Policy Bucket      #
#------------------------#
resource "google_storage_bucket" "policy_bucket" {
  name          = var.policy_bucket
  force_destroy = true
  versioning {
    enabled = true
  }
  bucket_policy_only = true
}

#-------------------------------------#
# Cloud Function Service Account      #
#-------------------------------------#
resource "google_service_account" "org_policy_compare_sa" {
  account_id   = "org-policy-compare"
  display_name = "Organization Policy Compare"
}

#----------------------------------------------#
# Cloud Function Service Account IAM Role      #
#----------------------------------------------#
resource "google_organization_iam_custom_role" "org_policy_compare_custom_role" {
  role_id     = "org_policy_compare_cfn"
  org_id      = var.org_id
  title       = "Organization Policy Function Role"
  description = "IAM role for Cloud Function to Compare Org Policies"
  permissions = var.function_perms
}

#------------------------------------------------#
# Cloud Function Service Account IAM Member      #
#------------------------------------------------#
resource "google_organization_iam_member" "org_policy_compare_member" {
  org_id = var.org_id
  role   = "organizations/${var.org_id}/roles/${google_organization_iam_custom_role.org_policy_compare_custom_role.role_id}"
  member = "serviceAccount:${google_service_account.org_policy_compare_sa.email}"
}

#---------------------#
# Architecture Module #
#---------------------#
module "pubsub_scheduled_example" {
  source = "terraform-google-modules/scheduled-function/google"
  providers = {
    google = google-beta
  }

  project_id = var.project_id
  region     = var.region

  function_entry_point                        = var.function_entry_point
  function_source_directory                   = var.function_source_directory
  function_name                               = var.function_name
  function_available_memory_mb                = var.function_available_memory_mb
  function_description                        = var.function_description
  function_event_trigger_failure_policy_retry = var.function_event_trigger_failure_policy_retry
  function_runtime                            = var.function_runtime
  function_timeout_s                          = var.function_timeout_s
  function_service_account_email              = google_service_account.org_policy_compare_sa.email

  topic_name      = var.topic_name
  job_description = var.job_description
  job_name        = var.job_name
  job_schedule    = var.job_schedule
  scheduler_job   = var.scheduler_job

  bucket_force_destroy = var.bucket_force_destroy
  bucket_name          = var.function_bucket
  message_data         = var.message_data
  time_zone            = var.time_zone
  function_environment_variables = {
    POLICY_BUCKET            = var.policy_bucket
    FILE_LOCATION            = var.file_location
    POLICY_FILE              = var.policy_file
    ORG_ID                   = var.org_id
    S_PROJECT                = var.secret_project
    S_SLACK_NAME             = var.secret_slack_name
    S_TOKEN_NAME             = var.secret_token_name
    S_VERSION                = var.secret_version == "" ? "latest" : var.secret_version
    CONSUMER_KEY_NAME        = var.consumer_key_name
    CONSUMER_KEY_SECRET_NAME = var.consumer_key_secret_name
    ACCESS_TOKEN_NAME        = var.access_token_name
    ACCESS_TOKEN_SECRET_NAME = var.access_token_secret_name
  }
}
