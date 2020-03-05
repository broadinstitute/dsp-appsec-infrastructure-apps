resource "google_service_account" "sa" {
  account_id   = var.account_id
  display_name = var.display_name
}

resource "google_project_iam_member" "role_member" {
  for_each = toset(var.roles)

  role   = "roles/${each.key}"
  member = "serviceAccount:${google_service_account.sa.email}"
}

output "name" {
  value = google_service_account.sa.name
}

output "email" {
  value = google_service_account.sa.email
}
