FROM python:slim

RUN apt-get update -q && \
    apt-get upgrade -qq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /zap

COPY src/requirements.txt .
RUN pip install --upgrade -r requirements.txt

COPY src/*.py ./

ENTRYPOINT ["python3", "-u", "main.py"]
