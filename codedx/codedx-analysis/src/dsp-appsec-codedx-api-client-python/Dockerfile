FROM python:alpine3.7
RUN addgroup -S codedxuser && adduser -S -G codedxuser codedxuser
COPY . /app/
WORKDIR /app/
RUN pip install -r requirements.txt
RUN python3 setup.py install
EXPOSE 5000
USER codedxuser
WORKDIR /app/examples/
ENTRYPOINT ["python3"]