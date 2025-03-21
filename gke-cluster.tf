provider "google" {
  project = "k8-assignment-453622"
  region  = "us-central1"
  zone    = "us-central1-a"
}

resource "google_container_cluster" "initial_terraform_cluster" {
  name     = "my-gke-cluster"
  location = "us-central1"
  zone  = "us-central1-a"

  remove_default_node_pool = true
  initial_node_count       = 1
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "my-node-pool"
  cluster    = google_container_cluster.initial_terraform_cluster.id
  location   = google_container_cluster.initial_terraform_cluster.location
  zone = google_container_cluster.initial_terraform_cluster.zone
  node_count = 1

  node_config {
    machine_type = "e2-micro"
    disk_size_gb = 10
    disk_type    = "pd-standard"  # Set the disk type to pd-standard
    image_type   = "COS_CONTAINERD"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

//Removed prev code beacause i don't need GKE storage ssd and PVC, instead i have a disk of type pd-standard which will be attached with node and can be used by containers in the same pod

# Create a Google Cloud Disk
resource "google_compute_disk" "default" {
  name  = "bindu-disk"
  type  = "pd-standard"
  zone  = "us-central1-a"
  size  = 10
}