# Use the latest golang mirror to compile to a binary
FROM mirror.gcr.io/library/golang AS build

ARG VERSION="1.18-dev"
ARG PROXY_SRC="github.com/GoogleCloudPlatform/cloudsql-proxy/cmd/cloud_sql_proxy"

RUN go get ${PROXY_SRC}
WORKDIR /go/src/${PROXY_SRC}

COPY sqlscope.patch .
RUN git apply --ignore-space-change sqlscope.patch
RUN go build -ldflags "-X 'main.versionString=$VERSION'" -o /cloud_sql_proxy

# Final Stage
FROM gcr.io/distroless/base-debian10:nonroot
COPY --from=build --chown=nonroot /cloud_sql_proxy /cloud_sql_proxy
USER nonroot
