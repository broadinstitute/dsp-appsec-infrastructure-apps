FROM python:3
WORKDIR /upload-worker
COPY src/requirements.txt .
RUN pip install --upgrade -r requirements.txt
COPY src/*.py .
ENTRYPOINT ["python3", "-u", "worker.py"]
