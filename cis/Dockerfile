ARG USER="inspec"

FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian AS base

ARG USER

ENV CHEF_LICENSE="accept-no-persist"

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git-core \
        ruby-dev \
        ruby \
    && \
    pip3 install -Ur requirements.txt \
    && \
    gem install inspec-bin -v 4.48.3 -qN && \
    git clone --depth 1 https://github.com/GoogleCloudPlatform/inspec-gcp-cis-benchmark.git && \
    git clone --depth 1 https://github.com/GoogleCloudPlatform/inspec-gke-cis-benchmark.git && \
    mv inspec-gke-cis-benchmark/inspec-gke-cis-gcp . && \
    mv inspec-gke-cis-benchmark/inspec-gke-cis-k8s . \
    && \
    apt-get remove -y \
        build-essential \
        git-core \
        ruby-dev \
    && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* \
    && \
    useradd -m "${USER}" && \
    mkdir .inspec && \
    chown "${USER}" .inspec inspec-*-cis-*


FROM base AS test

RUN pip3 install -U pylint pytest

COPY *.py /

RUN pylint --disable=W0702,W0613,E0611,C0301,E1101,R0913,W1309,C0209 /*.py

RUN pytest /entrypoint_test.py



FROM base

ARG USER

ENV RUBYOPT="-W:no-deprecated"

COPY entrypoint.py scanweekly.py /

USER ${USER}

ENTRYPOINT [ "/entrypoint.py" ]
