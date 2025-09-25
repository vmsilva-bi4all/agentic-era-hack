# Deployment

This directory contains the Terraform configurations for provisioning the necessary Google Cloud infrastructure for your agent.

The recommended way to deploy the infrastructure and set up the CI/CD pipeline is by using the `agent-starter-pack setup-cicd` command from the root of your project.

However, for a more hands-on approach, you can always apply the Terraform configurations manually for a do-it-yourself setup.

For detailed information on the deployment process, infrastructure, and CI/CD pipelines, please refer to the official documentation:

**[Agent Starter Pack Deployment Guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment.html)**


# Development Notes

## 1. Choose the environment

There are two Terraform environments:

* Root (`deployment/terraform`) – staging + prod + CI/CD resources. Uses `vars/env.tfvars`.
* Dev (`deployment/terraform/dev`) – isolated dev infra (DB, buckets, etc.). Uses `dev/vars/env.tfvars`.

Work from the directory that matches what you want to deploy.

## 2. Authenticate to Google Cloud

Make sure you are logged in and the correct project is set (example uses the dev project):

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project hack-agentic-era-dev
```

## 3. (First time only) Create the remote state bucket(s)

Terraform's GCS backend expects the bucket to already exist.

Dev backend bucket (from `dev/backend.tf`): `hack-agentic-era-dev-terraform-state`

Prod/staging backend bucket (from `backend.tf`): `hack-agentic-era-prd-terraform-state`

Create if missing (adjust region as desired):

```powershell
gsutil mb -l us-central1 -b on gs://hack-agentic-era-dev-terraform-state
gsutil mb -l us-central1 -b on gs://hack-agentic-era-prd-terraform-state
```

If they already exist you can ignore any "bucket already exists" error.

## 4. Initialize Terraform (required before plan/apply)

Run this inside the folder you chose in step 1.

Dev environment:
```powershell
cd deployment/terraform/dev
terraform init
```

Root (staging/prod + CICD) environment:
```powershell
cd deployment/terraform
terraform init
```

If you changed backend settings and need to force reconfiguration:
```powershell
terraform init -reconfigure
```

## 5. Validate and plan

Dev:
```powershell
cd deployment/terraform/dev
terraform plan --var-file=vars/env.tfvars
```

Root (staging/prod + CICD):
```powershell
cd deployment/terraform
terraform plan --var-file=vars/env.tfvars
```

## 6. Apply

Only apply after reviewing the plan output:
```powershell
terraform apply --var-file=vars/env.tfvars
```

## 7. Common issues

Backend initialization required: Run `terraform init` (or `terraform init -reconfigure` if the backend block changed) in the correct directory before `plan`.

Bucket not found: Create the bucket as shown in step 3.

Insufficient permissions: Ensure your active account has `storage.admin` (for bucket creation) and necessary project IAM roles.

Provider credentials errors: Re-run `gcloud auth application-default login`.

## 8. Cleaning up

To see what would be destroyed:
```powershell
terraform plan -destroy --var-file=vars/env.tfvars
```

Then:
```powershell
terraform destroy --var-file=vars/env.tfvars
```

---

Tip: Avoid copying or editing the generated `terraform.tfstate` file manually. Let Terraform manage it in the GCS backend.