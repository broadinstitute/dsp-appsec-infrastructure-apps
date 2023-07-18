FROM us.gcr.io/broad-dsp-gcr-public/base/python:alpine AS base

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip install "Cython<3.0" pyyaml --no-build-isolation
RUN pip3 install -r requirements.txt

FROM base AS test

RUN pip3 install mypy pylint pytest

COPY *.py /

RUN mypy --ignore-missing-imports /*.py && \
    pylint /*.py && \
    pytest /*.py


FROM base

COPY entrypoint.py /

USER nobody

ENTRYPOINT [ "/entrypoint.py" ]
