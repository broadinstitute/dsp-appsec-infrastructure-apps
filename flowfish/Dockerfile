FROM python:3.7-alpine

COPY requirements.txt .
COPY flowfish/scan.sh flowfish/entrypoint.py / 

RUN apk add --no-cache \
        build-base \
        git \
        python3 \
        python3-dev \
        nmap \ 
        nmap-scripts \
    && pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && git clone https://github.com/vulnersCom/nmap-vulners \ 
        /usr/share/nmap/scripts/vulners \
    && nmap --script-updatedb \
    && rm -f /var/cache/apk/* \
    && chmod +x /scan.sh 

ENTRYPOINT ["/bin/sh", "-c", "/scan.sh"]
