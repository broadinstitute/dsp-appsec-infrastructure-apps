#!/usr/bin/env bash

set -eu

gosu www-data /usr/bin/dotnet "Ramper.dll" &

exec /docker-entrypoint.sh nginx -g "daemon off;"
