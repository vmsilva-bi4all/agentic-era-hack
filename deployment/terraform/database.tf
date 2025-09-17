
# resource "google_sql_database_instance" "main" {
#   project          = var.dev_project_id
#   name             = "hero-db-instance"
#   database_version = "POSTGRES_17"
#   region           = var.region

#   settings {
#     tier = "db-f1-micro"
#     edition = "ENTERPRISE"
#     ip_configuration {
#       ipv4_enabled = true
#       authorized_networks {
#         name  = "all"
#         value = "0.0.0.0/0"
#       }
#     }
#   }
# }

# # resource "google_sql_database_instance" "main" {
# #   project           = var.project_id
# #   name              = "agentic-extract"
# #   database_version  = "POSTGRES_16"
# #   region            = var.default_region
# #   settings {
# #     tier                        = "db-custom-1-3840"
# #     edition                     = "ENTERPRISE"
# #     availability_type           = "ZONAL"
# #     activation_policy           = "ALWAYS"
# #     backup_configuration {
# #       enabled                         = true
# #       location                        = "eu"
# #       point_in_time_recovery_enabled  = true
# #     }
# #     ip_configuration {
# #       ipv4_enabled = true
      
# #       # Authorize external IPs
# #       dynamic "authorized_networks" {
# #         for_each = var.cloud_sql_authorized_external_ips
# #         content {
# #           name  = "external-ip-${authorized_networks.key}"
# #           value = authorized_networks.value
# #         }
# #       }

# #       ## Private CONFIG: 
# #       #ipv4_enabled = false
# #       private_network = google_compute_network.vpc_network.self_link
# #     }

# #   }

# resource "google_sql_database" "hero_db" {
#   project  = var.dev_project_id 
#   name     = "hero_db"
#   instance = google_sql_database_instance.main.name
# }

# resource "google_sql_user" "hero_user" {
#   project = var.dev_project_id
#   #name     = "hero_db_user"
#   name     = google_secret_manager_secret_version.cloudsql_user.secret_data
#   instance = google_sql_database_instance.main.name
#   #password = random_password.cloudsql_password.result
#   password = google_secret_manager_secret_version.cloudsql_password.secret_data
# }

# # Secret - User
# resource "google_secret_manager_secret" "cloudsql_user" {
#   project = var.dev_project_id
#   secret_id = "hero-cloudsql-user"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret_version" "cloudsql_user" {
#   secret      = google_secret_manager_secret.cloudsql_user.id
#   secret_data = "hero_db"
# }

# # Secret - Password 

# resource "random_password" "cloudsql_password" {
#   length  = 16
#   special = true
# }

# resource "google_secret_manager_secret" "cloudsql_password" {
#   project = var.dev_project_id
#   secret_id = "hero-cloudsql-password"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret_version" "cloudsql_password" {
#   secret      = google_secret_manager_secret.cloudsql_password.id
#   secret_data = random_password.cloudsql_password.result
# }

# # Secret - Host 

# resource "google_secret_manager_secret" "cloudsql_host" {
#   project = var.dev_project_id
#   secret_id = "hero-cloudsql-host"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret_version" "cloudsql_host" {
#   secret      = google_secret_manager_secret.cloudsql_host.id
#   #secret_data = "hero-db-instance"
#   secret_data = google_sql_database_instance.main.public_ip_address
# }

# # Secret - Port 

# resource "google_secret_manager_secret" "cloudsql_port" {
#   project = var.dev_project_id
#   secret_id = "hero-cloudsql-port"
#   replication {
#     auto {}
#   }
# }

# resource "google_secret_manager_secret_version" "cloudsql_port" {
#   secret      = google_secret_manager_secret.cloudsql_port.id
#   secret_data = "5432"
# }





# output "hero_postgres_instance_connection_name" {
#   value = google_sql_database_instance.main.connection_name
# }

# output "hero_postgres_instance_ip" {
#   value = google_sql_database_instance.main.public_ip_address
# }







# ############################

# # data "google_secret_manager_secret_version" "pgsql_db_user" {
# #   project = var.project_id
# #   secret = "AGENTIC_EXTRACT_PGSQL_DB_USER" 
# # }

# # data "google_secret_manager_secret_version" "pgsql_db_password" {
# #   project = var.project_id
# #   secret = "AGENTIC_EXTRACT_PGSQL_DB_PASSWORD" 
# # }



# #   root_password = data.google_secret_manager_secret_version.pgsql_db_password.secret_data

# #   deletion_protection = false

# #   lifecycle {
# #       ignore_changes = [
# #         #settings.0.ip_configuration
# #         settings[0].tier,  # Alternative syntax 
# #       ]
# #   }

# # }

# # resource "google_sql_database" "finsolutia_documents_pt" {
# #   name     = "finsolutia_documents_pt"
# #   instance = google_sql_database_instance.main.name
# # }

# # resource "google_sql_database" "finsolutia_documents_es" {
# #   name     = "finsolutia_documents_es"
# #   instance = google_sql_database_instance.main.name
# # }

# # resource "google_sql_user" "additional_user" {
# #   name     = data.google_secret_manager_secret_version.pgsql_db_user.secret_data
# #   instance = google_sql_database_instance.main.name
# #   password = data.google_secret_manager_secret_version.pgsql_db_password.secret_data
# # }



# #resource "null_resource" "create_db_and_tables" {
# #  provisioner "local-exec" {
# #    command = <<EOT
# #      PGPASSWORD=$(terraform output -raw instance_password) psql -h $(terraform output -raw instance_public_ip) -U $(terraform output -raw instance_user) -d document_archives <<-EOSQL
# #        -- Create schema
# #        CREATE SCHEMA IF NOT EXISTS document_archives AUTHORIZATION postgres;
# #
# #        -- Create document_files table
# #        CREATE TABLE IF NOT EXISTS document_archives.document_files (
# #          id serial4 NOT NULL,
# #          filename varchar(255) NOT NULL,
# #          md5checksum varchar(255) NULL,
# #          "type" varchar(255) NOT NULL,
# #          CONSTRAINT document_files_pkey PRIMARY KEY (id)
# #        );
# #
# #        -- Create documents_control table
# #        CREATE TABLE IF NOT EXISTS document_archives.documents_control (
# #          id serial4 NOT NULL,
# #          filename varchar(255) NOT NULL,
# #          md5checksum varchar(255) NULL,
# #          index_id varchar(255) NOT NULL,
# #          "action" varchar(20) NOT NULL,
# #          "timestamp" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
# #          CONSTRAINT documents_control_pkey PRIMARY KEY (id)
# #        );
# #      EOSQL
# #    EOT
# #  }
# #
# #  depends_on = [
# #    google_sql_database.document_archives,
# #    google_sql_user.additional_user
# #  ]
# #}
# #
# #output "instance_public_ip" {
# #  value = google_sql_database_instance.chatbot_postgres.public_ip_address
# #}
# #
# #output "instance_user" {
# #  value = data.google_secret_manager_secret_version.pgsql_db_user.secret_data
# #  sensitive = true
# #}
# #
# #output "instance_password" {
# #  value = data.google_secret_manager_secret_version.pgsql_db_password.secret_data
# #  sensitive = true
# #}