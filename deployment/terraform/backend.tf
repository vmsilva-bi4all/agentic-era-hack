terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-01-268885fdf398-terraform-state"
    prefix = "agentic-era-hack/prod"
  }
}
