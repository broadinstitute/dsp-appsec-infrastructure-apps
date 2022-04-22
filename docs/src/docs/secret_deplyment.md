---
id: secret_deployment
title: Secret deployment for each app
---

Values must be encoded. 

### Sdarq secrets
 
 '''
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
 '''

### CodeDx secrets


### ZAP Scanner secrets


### CIS Scanner secrets


### DefectDojo secrets