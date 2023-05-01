# DSP AppSec Infrastructure Apps

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=broadinstitute_dsp-appsec-infrastructure-apps&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=broadinstitute_dsp-appsec-infrastructure-apps)

This repository hosts DSP AppSec internal infrastructure deployed in GCP Kubernetes.
Check the documentation in this [link](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/). 

### Apps

- [Sdarq](sdarq) - `Sdarq` is a coordination platform to guide both developers and appsec professionals through an SDLC and provide interfaces into various tools and bind them.  Learn more in this [link](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/docs/sdarq).

<img src="https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/blob/sdarq-jtra-improvement/sdarq/frontend/src/assets/sdarq_app.png">
- [CIS Scanner](cis) - Security scanner that assess security posture of GCP projects. 
- [Automated ZAP Scanner](zap) - Scripts running in GKE as Cronjobs to scan a specific list of endpoints.
- [DefectDojo](defectdojo)
- [CodeDx](codedx)
- [Job Batch Dispatcher](batch)


### Questions
`appsec@broadinstitute.org`

