FROM gcr.io/cloud-builders/kubectl

RUN apt-get update -q && \
    apt-get install -qq --no-install-recommends gettext && \
    rm -rf /var/lib/apt/lists/*
