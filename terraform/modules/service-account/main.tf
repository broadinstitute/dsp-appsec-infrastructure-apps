resource "google_service_account" "sa" {
  account_id   = var.account_id
  display_name = var.display_name
}

resource "google_project_iam_member" "role_member" {
  count = length(var.roles)

  project = var.project
  role    = var.roles[count.index]
  member  = "serviceAccount:${google_service_account.sa.email}"
}

output "name" {
  value = google_service_account.sa.name
}

output "email" {
  value = google_service_account.sa.email
}
