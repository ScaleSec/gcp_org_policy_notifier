######################
# GCS Backend Bucket #
######################

terraform {
  backend "gcs" {
    bucket = ""
    prefix = ""
  }
}