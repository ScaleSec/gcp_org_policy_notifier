######################
# GCS Backend Bucket #
######################

# The GCS bucket needs to be pre-existing
terraform {
  backend "gcs" {
    bucket = "scalesec-terraform-state-files"
    prefix = "gha-test/"
  }
}
