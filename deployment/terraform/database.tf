
resource "google_sql_database_instance" "main" {
  for_each = local.deploy_project_ids
  
  project          = each.value
  name             = "hero-db-instance"
  database_version = "POSTGRES_17"
  region           = var.region

  settings {
    tier = "db-f1-micro"
    edition = "ENTERPRISE"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
  }
}

resource "google_sql_database" "hero_db" {
  for_each = local.deploy_project_ids
  
  project  = each.value 
  name     = "hero_db"
  instance = google_sql_database_instance.main[each.key].name
}

resource "google_sql_user" "hero_user" {
  for_each = local.deploy_project_ids

  project  = each.value
  #name     = "hero_db_user"
  name     = google_secret_manager_secret_version.cloudsql_user[each.key].secret_data
  instance = google_sql_database_instance.main[each.key].name
  #password = random_password.cloudsql_password.result
  password = google_secret_manager_secret_version.cloudsql_password[each.key].secret_data
}

# Secret - DB name
resource "google_secret_manager_secret" "cloudsql_db_name" {
  project = var.dev_project_id
  secret_id = "hero-cloudsql-db-name"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_db_name" {
  secret      = google_secret_manager_secret.cloudsql_db_name.id
  secret_data = "hero_db"
}

# Secret - User
resource "google_secret_manager_secret" "cloudsql_user" {
  for_each = local.deploy_project_ids

  project  = each.value
  secret_id = "hero-cloudsql-user"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_user" {
  for_each = local.deploy_project_ids
  
  secret      = google_secret_manager_secret.cloudsql_user[each.key].id
  secret_data = "hero_db"
}

## Secret - Password 
resource "random_password" "cloudsql_password" {
  for_each = local.deploy_project_ids

  length  = 16
  special = true
}

resource "google_secret_manager_secret" "cloudsql_password" {
  for_each = local.deploy_project_ids
  
  project  = each.value
  secret_id = "hero-cloudsql-password"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_password" {
  for_each = local.deploy_project_ids

  secret      = google_secret_manager_secret.cloudsql_password[each.key].id
  secret_data = random_password.cloudsql_password[each.key].result
}

## Secret - Host 
resource "google_secret_manager_secret" "cloudsql_host" {
  for_each = local.deploy_project_ids

  project  = each.value
  secret_id = "hero-cloudsql-host"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_host" {
  for_each = local.deploy_project_ids

  secret      = google_secret_manager_secret.cloudsql_host[each.key].id
  secret_data = google_sql_database_instance.main[each.key].public_ip_address
}

## Secret - Port 
resource "google_secret_manager_secret" "cloudsql_port" {
  for_each = local.deploy_project_ids

  project  = each.value
  secret_id = "hero-cloudsql-port"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_port" {
  for_each = local.deploy_project_ids

  secret      = google_secret_manager_secret.cloudsql_port[each.key].id
  secret_data = "5432"
}

# Output - External IPs for all environments
output "hero_postgres_external_ips" {
  description = "External IP addresses of the Cloud SQL instances for all environments"
  value = {
    for env, instance in google_sql_database_instance.main : env => instance.public_ip_address
  }
}

output "hero_postgres_connection_names" {
  description = "Connection names for all Cloud SQL instances"
  value = {
    for env, instance in google_sql_database_instance.main : env => instance.connection_name
  }
}



