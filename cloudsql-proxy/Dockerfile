FROM debian:testing-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl jq && \
    rm -rf /var/lib/apt/lists/*

COPY --from=gcr.io/cloudsql-docker/gce-proxy /cloud_sql_proxy /cloud_sql_proxy
