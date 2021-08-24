# ZAP Weekly Scans

This repo sets up a weekly cron job in the GKE AppSec cluster against the list of endpoints downloaded from DefectDojo, then uploads results files to CodeDx. It runs `trigger.py` on a cron job (currently Sunday mornings at 7am). 

Uses [ZAP automation](https://www.zaproxy.org/docs/docker/) to run the scans. Target endpoints are tagged in Defect Dojo with a scan type and this automation scans according to the type tagged.



# Troubleshooting and Testing

## Get Endpoints

Download endpoint list in JSON from Defect Dojo:

```sh
curl -L  -H  "accept: application/json" -H "Authorization: Token ${DOJO_TOKEN}" "https://defectdojo.dsp-appsec.broadinstitute.org/api/v2/endpoints?limit=100"
```

## Run Scans

This runs the ZAP automation directly, bypassing the wrapper scripts in this repo.

```sh
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t ${ENDPOINT}
```
