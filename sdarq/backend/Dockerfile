FROM python:slim

RUN  pip install --upgrade pip 

WORKDIR /app
COPY sdarq/backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --from=owasp/zap2docker-weekly /zap/zap_common.py ./
COPY sdarq/backend/src/*.py zap/src/*.py ./

ENV PORT 8080
ENTRYPOINT [ \
  "gunicorn", \
  "--workers", "5", \
  "--worker-tmp-dir", "local", \
  "--worker-connections", "1000", \
  "--timeout", "360", \
  "--graceful-timeout", "360", \
  "--limit-request-line", "8190", \
  "--limit-request-fields", "25", \
  "-b", "0.0.0.0:8080", \
  "app:app" \
]
