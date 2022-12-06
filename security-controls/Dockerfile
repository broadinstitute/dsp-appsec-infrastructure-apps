FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian AS base

COPY requirements.txt .

RUN apt-get update -q && \
    apt-get install -qq --no-install-recommends \
      build-essential \
      libffi-dev && \
    pip3 install -U pip && \
    pip3 install -r requirements.txt && \
    apt-get remove -y \
      build-essential \
      libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY *.py ./