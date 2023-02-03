## SDARQ Security Controls

<img src="https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/blob/master/sdarq/frontend/src/assets/sdarq_security_controls.png">

This folder contains scripts that run as `cronjobs` in the GKE cluster. These cronjobs:
- auto update security controls in SDARQ (DAST, 3rd party dependencies scan, and SAST)
- report to AppSec team all security controls that are missing for specific services. If AppSec team decides to mark them as False Positives, they can add `SERVICENAME_SECURITYCONTROL` by comma in `_SECURITY_CONTROLS_IGNORE` variable in cloud build trigger. For example if service A is missing DAST scan, it can be added to `_SECURITY_CONTROLS_IGNORE` as `A_zap`. If service B is missing CIS scanner, it can be added to `_SECURITY_CONTROLS_IGNORE` as `A_zap,B_cis_scanner`.

This is part of SDARQ, but is is deployed as a different namespace `security-controls` in GKE cluster.



