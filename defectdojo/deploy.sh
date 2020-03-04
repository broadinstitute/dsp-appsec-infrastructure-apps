#!/usr/bin/env sh

export PROJECT_ID="$(gcloud config get-value project)"
export DNS_HOSTNAME="defectdojo.dsp-appsec.broadinstitute.org"
export DOJO_DOCKER="us.gcr.io/${PROJECT_ID}/defectdojo-django"

export DD_DATABASE_TYPE="postgres"
export DD_DATABASE_ENGINE="django.db.backends.postgresql_psycopg2"
export DD_DATABASE_NAME="defectdojo"
export DD_DATABASE_USER="defectdojo"
export DD_DATABASE_PORT="5432"

export DD_CELERY_BROKER_USER="celery"

export DD_ADMIN_FIRST_NAME="AppSec"
export DD_ADMIN_LAST_NAME="Admin"
export DD_ADMIN_MAIL="appsec@broadinstitute.org"
export DD_ADMIN_USER="admin"

export SQL_INSTANCE="defectdojo-sql"
export SQL_REGION="us-east1"
export SQL_TIER="db-custom-1-3840"
export SQL_VERSION="POSTGRES_11"

envsubst < "deploy.yaml" | kubectl apply -f -
