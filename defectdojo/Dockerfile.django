FROM defectdojo/defectdojo-django

COPY django.patch /tmp

RUN git apply /tmp/django.patch
