FROM us.gcr.io/broad-dsp-gcr-public/base/python:debian

WORKDIR /app
COPY sdarq/backend/requirements.txt requirements.txt

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


COPY --from=owasp/zap2docker-weekly /zap/zap_common.py ./
COPY sdarq/backend/src/*.py zap/src/*.py ./

ENV PORT 8080
ENTRYPOINT [ \
  "gunicorn", \
  "--workers", "5", \
  "--worker-tmp-dir", "/dev/shm", \
  "--worker-connections", "1000", \
  "--timeout", "360", \
  "--graceful-timeout", "360", \
  "--limit-request-line", "8190", \
  "--limit-request-fields", "30", \
  "-b", "0.0.0.0:8080", \
  "app:app" \
]
