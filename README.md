# GCP Organization Policy Notifier




## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| bucket\_force\_destroy | When deleting the GCS bucket containing the cloud function, delete all objects in the bucket first. | `bool` | `true` | no |
| file\_location | Location to store the org policy file in the Cloud Function. Needs to be in /tmp/. | `string` | n/a | yes |
| function\_available\_memory\_mb | The amount of memory in megabytes allotted for the function to use. | `number` | `2048` | no |
| function\_bucket | The GCS bucket that stores the Cloud Function. | `string` | n/a | yes |
| function\_description | The description of the function. | `string` | `"Compares Org Policies and alerts users."` | no |
| function\_entry\_point | The name of a method in the function source which will be invoked when the function is executed. | `string` | `"announce_kickoff"` | no |
| function\_event\_trigger\_failure\_policy\_retry | A toggle to determine if the function should be retried on failure. | `bool` | `false` | no |
| function\_name | The name to apply to the function. | `string` | n/a | yes |
| function\_perms | The Cloud Function custom IAM role permissions. Must be a list. | `list` | <pre>[<br>  "secretmanager.secrets.get",<br>  "secretmanager.versions.get",<br>  "secretmanager.versions.access",<br>  "orgpolicy.policy.get",<br>  "resourcemanager.projects.get",<br>  "resourcemanager.projects.list",<br>  "storage.objects.create",<br>  "storage.objects.get",<br>  "storage.objects.update",<br>  "storage.objects.delete",<br>  "storage.objects.list"<br>]</pre> | no |
| function\_runtime | The runtime in which the function will be executed. | `string` | `"python37"` | no |
| function\_source\_directory | The contents of this directory will be archived and used as the function source. | `string` | `"./src"` | no |
| function\_timeout\_s | The amount of time in seconds allotted for the execution of the function. | `number` | `60` | no |
| job\_description | The description of the Cloud Scheduler. | `string` | `"Starts Organization Policies check."` | no |
| job\_name | The name of the scheduled job to run. | `string` | n/a | yes |
| job\_schedule | The job frequency, in cron syntax. | `string` | `"0 9 * * *"` | no |
| message\_data | The data to send in the topic message. | `string` | `"U3RhcnRpbmcgQ29tcGFyaXNvbg=="` | no |
| org\_id | The GCP Org ID to assign permissions to. | `any` | n/a | yes |
| policy\_bucket | The GCS bucket that contains the Org policies. | `string` | n/a | yes |
| policy\_file | The name of the Org policy file in the GCS bucket. | `string` | n/a | yes |
| project\_id | The ID of the project where the resources will be created. | `string` | n/a | yes |
| region | The region in which resources will be applied. | `string` | n/a | yes |
| scheduler\_job | An existing Cloud Scheduler job instance. | `object({ name = string })` | `null` | no |
| secret\_name | The name of the Slack Webhook secret in GCP. | `any` | n/a | yes |
| secret\_project | The GCP project the Slack Webhook is stored. | `any` | n/a | yes |
| secret\_version | The version of the Slack Webhook secret in GCP. | `any` | n/a | yes |
| time\_zone | The timezone to use in scheduler. | `string` | `"America/Detroit"` | no |
| topic\_name | Name of pubsub topic connecting the scheduled job and the function. | `string` | n/a | yes |