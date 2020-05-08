#!/bin/bash 
set -e
# $1 = PROJECT
# $2 = BRANCH
# $3 = REPO
# $4 = SRCCLR_API_TOKEN_PATH
# $5 = ORG
# $6 = SCAN_SUBDIR

PATH=$PATH:/usr/share/sbt/bin

echo "${SRCCLR_API_TOKEN_PATH}"
gcloud auth list
export SRCCLR_API_TOKEN=$(gcloud secrets versions access latest --project="dsp-appsec-dev" --secret="sourceclear-${WORKSPACE}-api-token")
export GIT_TOKEN=$(gcloud secrets versions access latest --project="dsp-appsec-dev" --secret="github-test")

git init $PWD
git --version
git config remote.origin.url https://$GIT_TOKEN:x-oauth-basic@github.com/$ORG/$PROJECT.git
git fetch --tags --progress https://$GIT_TOKEN:x-oauth-basic@github.com/$ORG/$PROJECT.git +refs/heads/*:refs/remotes/origin/*
git checkout -f "$(git rev-parse $(git branch -a | grep $BRANCH | head -1))"
git tag -d $(git tag -l)

if [ "$PROJECT" == 'ORSP' ]; then
 echo "gradle SCAN"
 curl -sSL https://www.sourceclear.com/install | bash
 #srcclr activate
 cat <<EOT >> build.gradle

 srcclr {
  apiToken = "$SRCCLR_API_TOKEN" 
 }
 
EOT
 export SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN
 SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN SCAN_DIR=$PWD$SCAN_SUBDIR DEBUG=1 ./gradlew clean build srcclr 
elif [ "$PROJECT" == 'orsp-pub' ]; then
 echo "gradle SCAN"
 curl -sSL https://www.sourceclear.com/install | bash
 #srcclr activate
 cat <<EOT >> build.gradle

 srcclr {
  apiToken = "$SRCCLR_API_TOKEN" 
 }
 
EOT
 export SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN
 SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN SCAN_DIR=$PWD$SCAN_SUBDIR DEBUG=1 ./gradlew srcclr
elif [ "$PROJECT" == 'jade-data-repo' ]; then
 echo "gradle SCAN"
 curl -sSL https://www.sourceclear.com/install | bash
 #srcclr activate
 cat <<EOT >> build.gradle

 srcclr {
  apiToken = "$SRCCLR_API_TOKEN" 
 }
 
 
EOT
 export SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN
 #SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN SCAN_DIR=$PWD$SCAN_SUBDIR DEBUG=1 ./gradlew clean build srcclr
 SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN SCAN_DIR=$PWD$SCAN_SUBDIR srcclr scan --recursive --debug --allow-dirty
elif [ "$PROJECT" == 'cromwell' ]; then
 curl -sSL https://www.sourceclear.com/install | bash
 export SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN
 export SRCCLR_SCM_REF=$BRANCH
 #srcclr activate
 SRCCLR_API_TOKEN=$SRCCLR_API_TOKEN SCAN_DIR=$PWD$SCAN_SUBDIR DEBUG=1 srcclr scan --debug --scan-collectors sbt
elif [ "$PROJECT" == 'ddp-mmrf' ]; then
 echo "${PWD}""$SCAN_SUBDIR"
 cd "${PWD}""$SCAN_SUBDIR" || exit
 . ci/sourceclear-setup.sh
 curl -sSL https://download.sourceclear.com/ci.sh | DEBUG=1 sh 
elif [ "$PROJECT" == 'calhoun' ] || [ "$PROJECT" == 'secondary-analysis' ]; then
 echo "${PWD}""$SCAN_SUBDIR"
 cd "${PWD}""$SCAN_SUBDIR" || exit
 . ci/sourceclear-setup.sh
 curl -sSL https://download.sourceclear.com/ci.sh | DEBUG=1 sh 
elif [ "$PROJECT" == 'ddp' ]; then
 if [ "$SCAN_SUBDIR" == '/pepper-apis' ]; then
  export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-11.0.4.11-1.el7_7.x86_64
 fi
 echo "${PWD}""$SCAN_SUBDIR"
 cd "${PWD}""$SCAN_SUBDIR" || exit
 curl -sSL https://download.sourceclear.com/ci.sh | DEBUG=1 sh 
else 
 echo "PACKAGED SCAN"
 if [ "$PROJECT" == 'import-service' ]; then
  touch $PWD$SCAN_SUBDIR/srcclr.yml
  echo 'python_path: /usr/bin/python3.6' >> $PWD$SCAN_SUBDIR/srcclr.yml
 fi
 if [ "$PROJECT" == 'avram' ]; then
  wget https://storage.googleapis.com/appengine-sdks/featured/appengine-java-sdk-1.9.65.zip
  unzip appengine-java-sdk-1.9.65.zip
  export PATH=$PATH:appengine-java-sdk-1.9.65/bin/
  export APPENGINE_SDK_HOME=appengine-java-sdk-1.9.65
 fi
 curl -sSL https://download.sourceclear.com/ci.sh | SCAN_DIR=$PWD$SCAN_SUBDIR DEBUG=1 sh 
fi
