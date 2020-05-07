FROM debian:sid-slim AS base

ENV INSPEC_VERSION=4.18.51 \
    CHEF_LICENSE=accept-no-persist

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git-core \
        python3-dev \
        python3-pip \
        ruby-dev \
        ruby \
    && \
    pip3 install -r requirements.txt \
    && \
    gem install inspec-bin -qN -v "${INSPEC_VERSION}" && \
    git clone --depth 1 https://github.com/GoogleCloudPlatform/inspec-gcp-cis-benchmark.git \
    && \
    apt-get remove -y \
        build-essential \
        git-core \
        python3-dev \
        ruby-dev \
    && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/* \
    && \
    mkdir .inspec && \
    chown nobody .inspec inspec-gcp-cis-benchmark


FROM base AS test

RUN pip3 install  pytest

COPY *.py /

# RUN pylint /*.py
RUN pytest /*.py


FROM base

COPY entrypoint.py /

# USER nobody

ENTRYPOINT [ "/entrypoint.py" ]
