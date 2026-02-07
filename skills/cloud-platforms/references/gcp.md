# GCP Patterns

## GKE Best Practices

```hcl
resource "google_container_cluster" "main" {
  name     = var.cluster_name
  location = var.region

  # Enable Autopilot for managed nodes
  enable_autopilot = true

  # Or use standard mode with node pools
  # remove_default_node_pool = true
  # initial_node_count       = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.nodes.name

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }
}
```

## Workload Identity

```hcl
resource "google_service_account" "app" {
  account_id   = "app-sa"
  display_name = "Application Service Account"
}

resource "google_project_iam_member" "app_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.app.email}"
}

resource "google_service_account_iam_member" "workload_identity" {
  service_account_id = google_service_account.app.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.namespace}/app]"
}
```

## VPC Network

```hcl
resource "google_compute_network" "main" {
  name                    = "main-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "nodes" {
  name          = "gke-nodes"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }

  private_ip_google_access = true
}
```

## Cloud Storage

```hcl
resource "google_storage_bucket" "data" {
  name     = "app-data-bucket"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}
```

## Cloud SQL

```hcl
resource "google_sql_database_instance" "main" {
  name             = "app-database"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-custom-2-4096"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }

    maintenance_window {
      day  = 7
      hour = 3
    }
  }

  deletion_protection = true
}
```

## Secret Manager

```hcl
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "app_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app.email}"
}
```
