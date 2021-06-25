FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY trigger.py .
CMD [ "python3", "trigger.py"]