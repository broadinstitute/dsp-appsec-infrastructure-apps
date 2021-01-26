# Install ZAProxy

zaproxy_version="2.9.0"

apt-get update

apt-get install -y net-tools
apt-get -y install curl
apt-get install -y python3 python3-pip wget openjdk-8-jre-headless git

sed -i -e '/^assistive_technologies=/s/^/#/' /etc/java-*-openjdk/accessibility.properties
JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
export JAVA_HOME

pip3 install --upgrade pip python-owasp-zap-v2.4
pip3 install git+https://github.com/broadinstitute/dsp-appsec-codedx-api-client-python.git@b0bea14ef9f39df4e3abfb187ac7d2478ef8c865
pip3 install slackclient
pip3 install --upgrade google-cloud-storage
pip3 install --upgrade google-cloud-pubsub
pip3 install google-cloud-secret-manager
pip3 install google-cloud-tasks==1.5.0
pip3 install googleapis-common-protos==1.51.0
pip3 install httplib2
pip3 install oauth2client

wget https://github.com/zaproxy/zaproxy/releases/download/v"${zaproxy_version:?}"/ZAP_"${zaproxy_version:?}"_Linux.tar.gz

tar xvzf ZAP_"${zaproxy_version:?}"_Linux.tar.gz

mv ZAP_"${zaproxy_version:?}" zap