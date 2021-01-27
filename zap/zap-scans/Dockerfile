# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3
ENV APP_HOME /zap-scans
WORKDIR $APP_HOME
COPY src/requirements.txt .
RUN pip install --upgrade -r requirements.txt
COPY src/*.py ./
ENTRYPOINT ["python3", "-u", "main.py"]
