// Required variables
variable "project_id" {
  type        = string
  description = "The ID of the project where the resources will be created."
}

variable "name_prefix" {
  type        = string
  description = "The prefixed used to name resources"
}

variable "org_id" {
  description = "The GCP Org ID to assign permissions to."
}

variable "secret_project" {
  description = "The GCP project number where the Slack Webhook is stored."
}

variable "secret_slack_name" {
  description = "The name of the Slack Webhook secret in GCP."
}

variable "secret_token_name" {
  description = "The name of the GitHub token secret in GCP."
}

variable "twitter_consumer_key_name" {
  description = "The name of the Twitter Consumer Key secret in GCP."
}

variable "twitter_consumer_key_secret_name" {
  description = "The name of the Twitter Consumer Key Secret secret in GCP."
}

variable "twitter_access_token_name" {
  description = "The name of the Twitter Access Token secret in GCP."
}

variable "twitter_access_token_secret_name" {
  description = "The name of the Twitter Access Token Secret secret in GCP."
}

// Optional variables
variable "job_description" {
  type        = string
  description = "The description of the Cloud Scheduler."
  default     = "Starts Organization Policies check."
}

variable "job_schedule" {
  type        = string
  description = "The job frequency, in cron syntax. The default is every hour."
  default     = "0 * * * *"
}

variable "function_available_memory_mb" {
  type        = number
  default     = 2048
  description = "The amount of memory in megabytes allotted for the function to use."
}

variable "function_description" {
  type        = string
  default     = "Compares Org Policies and alerts users."
  description = "The description of the function."
}

variable "function_entry_point" {
  type        = string
  description = "The name of a method in the function source which will be invoked when the function is executed."
  default     = "announce_kickoff"
}

variable "function_event_trigger_failure_policy_retry" {
  type        = bool
  default     = false
  description = "A toggle to determine if the function should be retried on failure."
}

variable "function_runtime" {
  type        = string
  default     = "python37"
  description = "The runtime in which the function will be executed."
}

variable "function_source_directory" {
  type        = string
  description = "The contents of this directory will be archived and used as the function source."
  default     = "./src"
}

variable "function_timeout_s" {
  type        = number
  default     = 60
  description = "The amount of time in seconds allotted for the execution of the function."
}

variable "bucket_force_destroy" {
  type        = bool
  default     = true
  description = "When deleting the GCS bucket containing the cloud function, delete all objects in the bucket first."
}

variable "region" {
  type        = string
  description = "The region in which resources will be applied."
  default     = "us-central1"
}

variable "message_data" {
  type        = string
  description = "The data to send in the topic message."
  default     = "U3RhcnRpbmcgQ29tcGFyaXNvbg=="
}

variable "time_zone" {
  type        = string
  description = "The timezone to use in scheduler."
  default     = "America/Detroit"
}

variable "file_location" {
  type        = string
  description = "Location to store the org policy file in the Cloud Function. Needs to be in /tmp/."
  default     = "/tmp/policies.txt"
}

variable "policy_file" {
  type        = string
  description = "The name of the Org policy file in the GCS bucket."
  default     = "policies.txt"
}

variable "function_perms" {
  description = "The Cloud Function custom IAM role permissions. Must be a list."
  default     = ["secretmanager.secrets.get", "secretmanager.versions.get", "secretmanager.versions.access", "orgpolicy.policy.get", "resourcemanager.projects.get", "resourcemanager.projects.list", "storage.objects.create", "storage.objects.get", "storage.objects.update", "storage.objects.delete", "storage.objects.list"]
}

variable "secret_version" {
  description = "The version of the Slack Webhook secret in GCP. Leave as an empty string to use 'latest'"
  default     = "latest"
}

variable "scheduler_job" {
  type        = object({ name = string })
  description = "An existing Cloud Scheduler job instance."
  default     = null
}

