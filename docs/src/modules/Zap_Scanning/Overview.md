# Zap Scanning

As a part of the Application Security team's continuous monitoring processes, automated scans are run each week on using the OWASP ZAProxy. ZAProxy scans an endpoint by analyzing responses for vulnerabilities. An endpoint can refer to a webpage or an OpenAPI definition (represented by a YAML or JSON file).


Endpoints are stored in DefectDojo. There are also different scan types that allow users to run more active scans.


Scans are run using the Job Dispatcher pattern. After fetching a list of endpoints from DefectDojo, a CronJob will send messages to GCP's PubSub service with information about the endpoint, the scan type, the CodeDx project, and the Slack channel to contact. A GKE job will be created to run the scan and upload results to CodeDx and Slack if requested.

Users can also request a scan via SDARQ. Go to [https://sdarq.dsp-appsec.broadinstitute.org/scan-service](https://sdarq.dsp-appsec.broadinstitute.org/scan-service). Users can only scan endpoints listed in DefectDojo.

**Warning**
Tests can be destructive. You should only run tests against services you own.

## Quickstart

TODO