
resource "google_sql_database_instance" "hero_postgres" {
  name             = "hero-postgres-instance"
  database_version = "POSTGRES_14"
  region           = var.region

  settings {
    tier = "db-f1-micro"
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
  name     = "hero_human_resources"
  instance = google_sql_database_instance.hero_postgres.name
}

resource "random_password" "cloudsql_password" {
  length  = 16
  special = true
}

resource "google_secret_manager_secret" "cloudsql_password" {
  secret_id = "hero-cloudsql-password"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "cloudsql_password" {
  secret      = google_secret_manager_secret.cloudsql_password.id
  secret_data = random_password.cloudsql_password.result
}

resource "google_sql_user" "hero_user" {
  name     = "hero_user"
  instance = google_sql_database_instance.hero_postgres.name
  password = random_password.cloudsql_password.result
}

output "hero_postgres_instance_connection_name" {
  value = google_sql_database_instance.hero_postgres.connection_name
}

output "hero_postgres_instance_ip" {
  value = google_sql_database_instance.hero_postgres.public_ip_address
}
