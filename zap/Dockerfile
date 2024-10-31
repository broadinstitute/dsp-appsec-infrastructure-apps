FROM softwaresecurityproject/zap-stable AS zap

FROM us.gcr.io/broad-dsp-gcr-public/base/python:3.10-debian AS base

FROM base AS build

RUN apt-get update && \
    apt-get install -y --no-install-recommends -qq git-core && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    python3 -m venv /venv && \
    /venv/bin/pip3 install -U pip

COPY requirements.txt .
RUN /venv/bin/pip3 install -U -r requirements.txt

WORKDIR /zap

FROM build

COPY --from=zap /zap/zap_common.py ./
COPY src/*.py ./

FROM base

COPY --from=zap /zap/zap_common.py ./
COPY --from=build /venv /venv
COPY src/*.py ./

ENTRYPOINT ["/venv/bin/python3", "-u", "-m"]