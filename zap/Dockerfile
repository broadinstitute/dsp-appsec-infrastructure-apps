FROM python:alpine
WORKDIR /upload-worker
ADD src .
RUN pip install --upgrade -r requirements.txt
RUN chmod u+x worker.py
CMD ["python", "worker.py"]