FROM defectdojo/defectdojo-django

COPY *.patch /tmp

RUN git apply /tmp/*.patch
