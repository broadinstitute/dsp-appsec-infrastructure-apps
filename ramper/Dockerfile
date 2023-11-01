FROM nginx AS build

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
      unzip

COPY Ramper*.zip "Ramper.zip"
RUN unzip Ramper.zip


FROM nginx

ENV HOST=ramper \
    ASPNETCORE_ENVIRONMENT=Production \
    DOTNET_PRINT_TELEMETRY_MESSAGE=false

WORKDIR /var/www/${HOST}

COPY --from=build /RamperOnPrem* .

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
      apt-transport-https \
      wget \
    && \
    wget --max-redirect=0 https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages.deb && \
    dpkg -i packages.deb && \
    rm packages.deb \
    && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
      aspnetcore-runtime-6.0 \
      gosu && \
    apt-get install -y apt-transport-https && \
    apt-get install -y libc6-dev libgdiplus libx11-dev &&\
    rm -rf /var/cache/apt/lists && \
    ln -sf /etc/nginx/conf.d/appsettings.json appsettings.json

COPY *.license /usr/share/ramper/licenses

COPY *.template /etc/nginx/templates/
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
