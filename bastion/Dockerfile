FROM us.gcr.io/broad-dsp-gcr-public/base/nodejs:alpine AS base

RUN apk add --no-cache dante-server

COPY sockd.conf /etc

USER nobody

ENTRYPOINT ["sockd", "-p", "/tmp/sockd.pid"]
