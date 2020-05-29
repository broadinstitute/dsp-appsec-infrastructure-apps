ARG USER="inspec"

FROM debian:testing-slim AS base

ARG USER
ARG INSPEC_VERSION="<5"

ENV CHEF_LICENSE="accept-no-persist"

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
    gem install "inspec-bin:${INSPEC_VERSION}" -qN && \
    git clone --depth 1 https://github.com/GoogleCloudPlatform/inspec-gcp-cis-benchmark.git \
    && \
    apt-get remove -y \
        build-essential \
        git-core \
        python3-dev \
        ruby-dev \
    && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* \
    && \
    useradd -m "${USER}" && \
    mkdir .inspec && \
    chown "${USER}" .inspec inspec-gcp-cis-benchmark


FROM base AS test

RUN pip3 install pylint pytest

COPY *.py /

RUN pylint /*.py
RUN pytest /*.py


FROM base

ARG USER

COPY entrypoint.py /

USER ${USER}

ENTRYPOINT [ "/entrypoint.py" ]
