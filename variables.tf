variable "project_id" {
  type        = string
  description = "The ID of the project where the resources will be created"
}

variable "job_name" {
  type        = string
  description = "The name of the scheduled job to run"
}

variable "job_description" {
  type        = string
  description = "The description of the Cloud Scheduler."
  default     = "Starts Organization Policies check."
}

variable "job_schedule" {
  type        = string
  description = "The job frequency, in cron syntax"
  default     = "0 9 * * *"
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

variable "function_name" {
  type        = string
  description = "The name to apply to the function"
}

variable "region" {
  type        = string
  description = "The region in which resources will be applied."
}

variable "topic_name" {
  type        = string
  description = "Name of pubsub topic connecting the scheduled job and the function"
}

variable "message_data" {
  type        = string
  description = "The data to send in the topic message."
  default     = "R2VuZXJhdGluZyBSZXBvcnQ="
}

variable "time_zone" {
  type        = string
  description = "The timezone to use in scheduler"
  default     = "America/Detroit"
}

variable "policy_bucket" {
  type        = string
  description = "The GCS bucket that contains the Org policies."
}

variable "function_bucket" {
  type        = string
  description = "The GCS bucket that stores the Cloud Function"
}

variable "file_location" {
  type        = string
  description = "Location to store the org policy file in the Cloud Function. Needs to be in /tmp/"
}

variable "policy_file" {
  type        = string
  description = "The name of the Org policy file in the GCS bucket."
}

variable "function_perms" {
  description = "The Cloud Function custom IAM role permissions. Must be a list."
}

variable "org_id" {
  description = "The GCP Org ID to assign permissions to."
}

variable "scheduler_job" {
  type        = object({ name = string })
  description = "An existing Cloud Scheduler job instance"
  default     = null
}
