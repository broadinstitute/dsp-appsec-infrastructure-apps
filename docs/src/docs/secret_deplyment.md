---
id: secret_deployment
title: Secret deployment for each app
---

Secrets deployed for each namespace in the cluster. Values must be encoded. 

### SDARQ secrets
 
```
apiVersion: v1
data:
  appsec_jira_project_key: Appsec team Jira board Key
  appsec_slack_channel: Appsec team Slack channel to get notifications
  dojo_api_key: DefectDojo API key
  dojo_host_url: DefectDojo host link
  jira_api_token: Jira API token
  jira_instance: Jira host link
  jira_username: Jira username
  jtra_slack_channel: Slack channel to receive notifications for High risk Jira ticket
  slack_token: DefectDojo API key
kind: Secret
metadata:
  name: sdarq
  namespace: sdarq
type: Opaque
```

### SDARQ Security-Controls secrets
 
```
  DAST_LINK: DefectDojo part of the link after the product number that redirects to the list of DAST scan findings
  DEFECT_DOJO: DefectDojo host link
  DEFECT_DOJO_KEY: DefectDojo API key
  DEP_SCAN_LINK: DefectDojo part of the link after the product number that redirects to the list of 3rd party dependencies scan findings
  SLACK_CHANNEL: slack channel that reports to AppSec team all the security controls missing for services
  SLACK_TOKEN: slack token
kind: Secret
metadata:
  name: security-controls
  namespace: security-controls
type: Opaque
```

### CodeDx secrets

```
apiVersion: v1
data:
  DB_PASSWORD: Database password
  DB_ROOT_PASSWORD: Database root password
  SUPERUSER_PASSWORD: Superuser password
kind: Secret
metadata:
  name: codedx
  namespace: codedx
type: Opaque
```

### ZAP Scanner secrets

If you are using CODEDX to send your ZAP results, replace CODEDX API KEY with your CODEDX API KEY,
if you are not using CODEDX, replace CODEDX API KEY value with encoded value of `""`

```
apiVersion: v1
data:
  CODEDX_API_KEY: CodeDx API key
  DEFECT_DOJO: DefectDojo host
  DEFECT_DOJO_KEY: DefectDojo key
  DEFECT_DOJO_USER: DefectDojo token
  SLACK_TOKEN: SLack token
kind: Secret
metadata:
  name: zap-scans
  namespace: zap
type: Opaque
```

### CIS Scanner secrets

```
apiVersion: v1
data:
  SDARQ_HOST: SDARQ host link
  SLACK_CHANNEL_WEEKLY_REPORT: Slack channel where to send weekly reports
  SLACK_TOKEN: Slack token
kind: Secret
metadata:
  name: cis-scans
  namespace: cis
type: Opaque
```

### DefectDojo secrets

#### Google Oauth integration to DefectDojo

```
apiVersion: v1
data:
  oauth2_key: 
  oauth2_secret: 
kind: Secret
metadata:
  name: googleoauth2
  namespace: defectdojo
type: Opaque
```