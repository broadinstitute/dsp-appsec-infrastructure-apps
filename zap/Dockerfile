FROM python:slim AS base

# Set up a Python virtualenv in a "build" stage
FROM base AS build

RUN apt-get update && \
    apt-get install --no-install-recommends -qq git-core && \
    python3 -m venv /venv && \
    /venv/bin/pip3 install -U pip

# Install Python dependencies into the virtualenv
COPY requirements.txt .
RUN /venv/bin/pip3 install -U -r requirements.txt

WORKDIR /zap


# Check code for linting errors
FROM build

RUN /venv/bin/pip3 install -U git+https://github.com/PyCQA/pylint.git

COPY src/*.py ./

RUN /venv/bin/pylint ./*.py


# Copy the virtualenv and sources into the clean final image
FROM base

COPY --from=build /venv /venv
COPY src/*.py ./

ENTRYPOINT ["/venv/bin/python3", "-u", "-m"]
