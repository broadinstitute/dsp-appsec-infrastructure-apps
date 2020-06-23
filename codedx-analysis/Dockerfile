FROM python:alpine
RUN addgroup -S codedx && adduser -S -G codedx codedx
USER codedx
WORKDIR /upload-worker
COPY src .
RUN pip install --upgrade -r requirements.txt
RUN chmod u+x worker.py
CMD ["python", "worker.py"]
