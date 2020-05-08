#!/bin/bash
set -e
apt-get update && \
apt-get install -y nodejs \
    npm \
    zip \
    maven \
    openjdk-11-jdk sbt \
    wget \
    git \
    python3-pip

# install yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
apt install yarn -y yarn

# install scala
wget http://downloads.lightbend.com/scala/2.11.8/scala-2.11.8.deb && \
dpkg -i scala-2.11.8.deb && \
apt-get install -y scala && \
echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list && \
curl -sL "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2EE0EA64E40A89B84B2DF73499E82A75642AC823" | apt-key add && \
apt-get update && \
apt-get install -y sbt

pip3 install -r requirements.txt

