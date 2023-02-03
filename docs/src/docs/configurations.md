---
id: config
title: Configurations
---

In your Google project set up Cloud Build trigger. Check `cloudbuild.yaml` file for more information.

Add these to Substitution variables:
- `_ORG_VIEWER_SA_EMAIL`  email of an existing Service Account with Org Viewer role
- `_DNS_DOMAIN`  fully-resolved DNS domain name (e.g. appsec.example.org)
- `_DNS_ZONE` DNS zone name to be created/updated (e.g. appsec)
- `_CIS_CONTROLS_IGNORE` CIS controls rule to ignore
- `_SECURITY_CONTROLS_IGNORE` services to omit from missing security-control notifications
- `_CODACY_ORGS` in-scope Codacy organizations as a comma-delimited list
- `_SONAR_ORGS` in-scope SonarCloud organizations, as a comma-delimited list of mappings from GitHub to SonarCloud organization (e.g. `githuborg=sonarcloudorg,ghorg2=scorg2`)

![architecture](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/img/cloud_build_config.png)