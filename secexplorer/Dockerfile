FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian

RUN apt-get update -q && \
    apt-get install -qq --no-install-recommends \
      build-essential \
      libffi7 \
      libffi-dev && \
    pip3 install -U cartography python-dateutil && \
    apt-get remove -y \
      build-essential \
      libffi-dev && \
    rm -rf /var/lib/apt/lists/*

USER nobody
ENTRYPOINT ["cartography"]
