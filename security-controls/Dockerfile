FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian AS base

FROM base AS build

RUN apt-get update && \
    apt-get install --no-install-recommends -qq git-core && \
    python3 -m venv /venv && \
    /venv/bin/pip3 install -U pip 

COPY requirements.txt .
RUN /venv/bin/pip3 install -U -r requirements.txt

WORKDIR /security-controls

FROM build

COPY *.py ./

FROM base

COPY --from=build /venv /venv
COPY *.py ./

RUN chmod +x /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]