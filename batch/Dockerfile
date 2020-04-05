FROM debian:sid-slim AS base

COPY requirements.txt .

RUN apt update && \
    apt install -y --no-install-recommends \
        build-essential \
        python3-dev \
        python3-pip \
    && \
    pip3 install -r requirements.txt \
    && \
    apt remove -y \
        build-essential \
        python3-dev \
    && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/*


FROM base AS test

RUN pip3 install pytest

COPY *.py /

RUN pytest /*.py


FROM base

COPY entrypoint.py /

USER nobody

ENTRYPOINT [ "/entrypoint.py" ]
