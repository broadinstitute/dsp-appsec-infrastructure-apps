for row in $(bq query --format=prettyjson "SELECT * FROM cis.dsp_appsec_sourceclear_repos"  | jq -r '.[] | @base64'); do
    _jq() {
        echo ${row} | base64 --decode | jq -r ${1}
    }

    export PROJECT=$(_jq '.project')
    export ORG=$(_jq '.org')
    export BRANCH=$(_jq '.branch')
    export SUBDIR=$(_jq '.subdir')
    export WORKSPACE=$(_jq '.workspace') 

    gcloud pubsub topics publish ${TOPIC_NAME} \
        --attribute "CONTAINER_NAME=${ORG}-${PROJECT}${SUBDIR//[\/]/-}" \
        --attribute "WORKSPACE=${WORKSPACE}" \
        --attribute "PROJECT=${PROJECT}" \
        --attribute "BRANCH=${BRANCH}" \
        --attribute "REPO=${ORG}/${PROJECT}" \
        --attribute "ORG=${ORG}" \
        --attribute "SUBDIR=${SUBDIR}"
done