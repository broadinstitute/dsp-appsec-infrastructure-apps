# Set up a Python virtualenv in a "build" stage
FROM debian:10-slim AS build
RUN apt-get update && \
    apt-get install --no-install-recommends -qq \
      build-essential \
      git-core \
      python3-venv \
    && \
    python3 -m venv /venv && \
    /venv/bin/pip3 install --upgrade pip

# Install Python dependencies into the virtualenv
COPY requirements.txt .
RUN /venv/bin/pip3 install --upgrade -r requirements.txt

# Copy the virtualenv and sources into the minimal final image
FROM gcr.io/distroless/python3-debian10
WORKDIR /app

COPY --from=build /venv /venv
COPY src/*.py ./

ENTRYPOINT ["/venv/bin/python3", "-u", "main.py"]
