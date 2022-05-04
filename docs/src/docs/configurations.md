---
id: config
title: Configurations
---

In your Google project set up Cloud Build trigger. 

Set up 
- `_ORG_VIEWER_SA_EMAIL`  email of an existing Service Account with Org Viewer role
- `_DNS_DOMAIN`  fully-resolved DNS domain name (e.g. appsec.example.org)
- `_DNS_ZONE` DNS zone name to be created/updated (e.g. appsec)
- `_CIS_CONTROLS_IGNORE` CIS controls rule to ignore

![architecture](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/img/cloud_build_config.png)