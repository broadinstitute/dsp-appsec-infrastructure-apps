FROM alpine

RUN apk add --no-cache dante-server

COPY sockd.conf /etc

USER nobody

ENTRYPOINT ["sockd", "-p", "/tmp/sockd.pid"]
