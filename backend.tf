######################
# GCS Backend Bucket #
######################

# The GCS bucket needs to be pre-existing
terraform {
  backend "gcs" {
    bucket = ""
    prefix = ""
  }
}