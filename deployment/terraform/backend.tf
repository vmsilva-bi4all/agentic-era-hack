terraform {
  backend "gcs" {
    bucket = "hack-agentic-era-prd-terraform-state"
    prefix = "hack-agentic-era/prod"
  }
}
