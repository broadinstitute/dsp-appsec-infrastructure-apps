# Set up a Python virtualenv in a "build" stage
FROM python:3 AS build
RUN python3 -m venv /venv

# Install Python dependencies into the virtualenv
COPY requirements.txt .
RUN /venv/bin/pip install --upgrade -r requirements.txt

# Override target Python path
RUN ln -sf /venv/bin/python3 /usr/bin/python3

# Copy the virtualenv and sources into the minimal final image
FROM gcr.io/distroless/python3-debian10
WORKDIR /app

COPY --from=build /venv /venv
COPY src/*.py ./

ENTRYPOINT ["python3", "-u", "main.py"]
