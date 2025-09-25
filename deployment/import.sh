
# Aux script to import existing resources into Terraform state
# NOTE: draft, needs to be adapted to your project setup

terraform import --var-file=vars/env.tfvars google_bigquery_dataset.telemetry_logs_dataset[\"staging\"] projects/${STAGING_PROJECT_ID}/datasets/telemetry_logs