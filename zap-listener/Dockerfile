# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM ubuntu:bionic

# Copy local code to the container image.
ENV APP_HOME /zap-scans
WORKDIR $APP_HOME
COPY src .
# Install production dependencies.
RUN ./setup.sh

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD python3 main.py