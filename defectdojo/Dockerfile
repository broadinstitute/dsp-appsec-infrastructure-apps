FROM defectdojo/defectdojo-django as dd


FROM dd as build

USER root

WORKDIR /

COPY django.patch .

RUN git apply django.patch


FROM dd

COPY --from=build /app/dojo/management/commands/import_surveys.py /app/dojo/management/commands/import_surveys.py
COPY --from=build /entrypoint-initializer.sh /entrypoint-initializer.sh
