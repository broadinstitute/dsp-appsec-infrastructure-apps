#!/usr/bin/env sh

pass_gen() {
  LC_CTYPE=C tr -dc "a-z0-9" < /dev/urandom | head -c "$1"
}

export DD_DATABASE_PASSWORD=$(pass_gen 32)
export DD_CELERY_BROKER_PASSWORD=$(pass_gen 128)
export DD_SECRET_KEY=$(pass_gen 128)
export DD_CREDENTIAL_AES_256_KEY=$(pass_gen 128)
export DD_ADMIN_PASSWORD=$(pass_gen 32)

envsubst < "secrets.yaml" | kubectl apply -f -
