provider "google" {
  project = "k8-assignment-453622"
  region  = "us-central1"
}

resource "google_container_cluster" "initial_terraform_cluster" {
  name     = "my-gke-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "my-node-pool"
  cluster    = google_container_cluster.initial_terraform_cluster.id
  location   = google_container_cluster.gke_cluster.location
  node_count = 1

  node_config {
    machine_type = "e2-micro"
    disk_size_gb = 10
    image_type   = "COS_CONTAINERD"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Fetch the GKE cluster credentials
data "google_client_config" "default" {}

# Configure the Kubernetes provider
provider "kubernetes" {
  host = "https://${google_container_cluster.initial_terraform_cluster.endpoint}"
  token = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.initial_terraform_cluster.master_auth[0].cluster_ca_certificate)
}

# Create a Storage Class for SSDs
resource "kubernetes_storage_class" "ssd" {
  metadata {
    name = "ssd"
  }
  storage_provisioner = "kubernetes.io/gce-pd"
  parameters = {
    type = "pd-ssd"
  }
}

# Create a Persistent Volume Claim (PVC)
resource "kubernetes_persistent_volume_claim" "container1-pvc" {
  metadata {
    name = "container1-pvc"
  }
  spec {
    access_modes = ["ReadWriteOnce"]  # GCE Persistent Disks only support ReadWriteOnce
    resources {
      requests = {
        storage = "1Gi"
      }
    }
    storage_class_name = kubernetes_storage_class.ssd.metadata[0].name  # Use the SSD Storage Class
  }

  # Ensure the PVC is created only after the GKE cluster is ready
  depends_on = [google_container_cluster.initial_terraform_cluster]
}