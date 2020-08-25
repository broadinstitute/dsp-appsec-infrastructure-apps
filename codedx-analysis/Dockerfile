FROM python:3.7
WORKDIR /upload-worker
COPY src .
RUN pip install --upgrade -r requirements.txt
ENTRYPOINT ["./worker.py"]
