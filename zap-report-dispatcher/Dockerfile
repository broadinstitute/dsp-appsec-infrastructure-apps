FROM debian:9.5
RUN apt-get -qq update; \
    apt-get -qq -y upgrade; \
    apt-get -qq -y install python python-dev python-pip
WORKDIR /upload-worker
ADD src .
RUN pip install --upgrade -r requirements.txt
RUN chmod u+x worker.py
CMD ["python", "worker.py"]