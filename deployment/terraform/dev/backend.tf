terraform {
  backend "gcs" {
    bucket = "hack-agentic-era-dev-terraform-state"
    prefix = "hack-agentic-era/dev"
  }
}
