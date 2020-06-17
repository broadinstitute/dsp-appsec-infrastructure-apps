FROM python:alpine
WORKDIR /upload-worker
COPY src .
RUN pip install --upgrade -r requirements.txt
RUN chmod u+x worker.py
CMD ["python", "worker.py"]