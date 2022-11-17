FROM owasp/zap2docker-weekly AS zap

FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian AS base

FROM base AS build

RUN apt-get update && \
    apt-get install --no-install-recommends -qq git-core && \
    python3 -m venv /venv && \
    /venv/bin/pip3 install -U pip

COPY requirements.txt .
RUN /venv/bin/pip3 install -U -r requirements.txt

WORKDIR /zap

FROM build

RUN /venv/bin/pip3 install -U git+https://github.com/PyCQA/pylint.git

COPY --from=zap /zap/zap_common.py ./
COPY src/*.py ./

RUN /venv/bin/pylint --fail-under=9 --ignore=zap_common.py,defectdojo_apiv2.py  ./*.py

FROM base

COPY --from=zap /zap/zap_common.py ./
COPY --from=build /venv /venv
COPY src/*.py ./

ENTRYPOINT ["/venv/bin/python3", "-u", "-m"]