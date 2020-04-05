FROM alpine AS base

ENV INSPEC_VERSION=4.18.51 \
    CHEF_LICENSE=accept-no-persist

COPY requirements.txt .

RUN apk add --no-cache \
        build-base \
        git \
        python3 \
        ruby-dev \
        ruby-etc \
        ruby-io-console \
        ruby-webrick \
    && \
    pip3 install -r requirements.txt \
    && \
    gem install inspec-bin -qN -v "${INSPEC_VERSION}" && \
    git clone --depth 1 https://github.com/GoogleCloudPlatform/inspec-gcp-cis-benchmark.git \
    && \
    apk del \
        build-base \
        ruby-dev \
    && \
    mkdir .inspec && \
    chown nobody .inspec inspec-gcp-cis-benchmark


FROM base AS test

RUN pip3 install pytest

COPY *.py /

RUN pytest /*.py


FROM base

COPY entrypoint.py /

USER nobody

ENTRYPOINT [ "/entrypoint.py" ]
