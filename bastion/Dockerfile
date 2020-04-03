FROM alpine

COPY tinyproxy.conf.patch .

RUN apk add --no-cache tinyproxy && \
    patch -p1 < tinyproxy.conf.patch

ENTRYPOINT ["tinyproxy", "-d"]
