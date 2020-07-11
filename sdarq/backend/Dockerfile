FROM python:3.6-jessie

RUN apt-get update \
  && pip install --upgrade pip==20.1.1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY src/* /app/
RUN ls -al /app/

ENV PORT 8080
CMD ["gunicorn", "--workers", "5","--worker-connections","1000", "--timeout", "360", "--graceful-timeout", "360", "--limit-request-line", "8190", "--limit-request-fields", "20",  "-b", "0.0.0.0:8080", "app:app"]
