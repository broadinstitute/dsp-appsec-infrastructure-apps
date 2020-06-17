FROM python:3.6-jessie

RUN apt-get update \
  && pip install --upgrade pip==20.1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY * /app/
RUN ls -al /app/

CMD ["python3", "scanweekly.py"]
