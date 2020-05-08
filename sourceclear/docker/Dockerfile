FROM google/cloud-sdk:latest
COPY . /srcclr-scan/
WORKDIR /srcclr-scan/
RUN ./setup.sh
RUN useradd -ms /bin/bash srcclr
USER srcclr
CMD bash