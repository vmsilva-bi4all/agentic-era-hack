# Import AlloyDB network
terraform import --var-file=vars/env.tfvars google_alloydb_network.db_network["staging"] projects/${STAGING_PROJECT_ID}/locations/${STAGING_REGION}/alloydbNetworks/hero-db-network

# Import AlloyDB cluster
terraform import --var-file=vars/env.tfvars google_alloydb_cluster.db_cluster["staging"] projects/${STAGING_PROJECT_ID}/locations/${STAGING_REGION}/clusters/hero-db-cluster

# Import AlloyDB instance
terraform import --var-file=vars/env.tfvars google_alloydb_instance.db_instance["staging"] projects/${STAGING_PROJECT_ID}/locations/${STAGING_REGION}/clusters/hero-db-cluster/instances/hero-db-instance

# Import VPC network
terraform import --var-file=vars/env.tfvars google_compute_network.default[\"staging\"] projects/${STAGING_PROJECT_ID}/global/networks/hero-alloydb-network

terraform import --var-file=vars/env.tfvars google_compute_subnetwork.default["staging"] projects/qwiklabs-gcp-04-6db254dd6d5c/regions/us-central1/subnetworks/hero-alloydb-network

terraform import --var-file=vars/env.tfvars google_compute_global_address.private_ip_alloc[\"staging\"] projects/${STAGING_PROJECT_ID}/global/addresses/hero-private-ip

terraform import --var-file=vars/env.tfvars google_alloydb_cluster.session_db_cluster[\"staging\"]  projects/qwiklabs-gcp-04-6db254dd6d5c/locations/us-central1/clusters/hero-alloydb-cluster


terraform import --var-file=vars/env.tfvars 


terraform import --var-file=vars/env.tfvars google_alloydb_instance.session_db_instance[\"staging\"] projects/947782432904/locations/us-central1/clusters/hero-alloydb-cluster/instances/hero-alloydb-instance


#projects/qwiklabs-gcp-04-6db254dd6d5c/locations/us-central1/clusters/hero-alloydb-cluster
#terraform import --var-file=vars/env.tfvars google_cloud_run_v2_service.app_staging