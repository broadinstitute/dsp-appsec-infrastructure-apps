## SDARQ

`Sdarq` is a coordination platform to guide both developers and appsec professionals through an SDLC and provide interfaces into various tools and bind them.

<img src="https://github.com/broadinstitute/dsp-appsec-infrastructure-apps/blob/sdarq-jtra-improvement/sdarq/frontend/src/assets/sdarq_app.png">

It is using `AngularJs` framework for frontend and `Flask` framework for backend.
### Run it locally

#### Frontend
To run locally SDARQ frontend, go to `frontend` folder of SDARQ

Run:
- `npm install` or `npm i`
- `ng serve` , it will run in the port `4200` of your localhost


#### Backend 

To run locally SDARQ backend, go to `backend` folder of SDARQ

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Backend has a list of env variables that need to be exported with their values.
```
  export appsec_jira_project_key="Appsec team Jira board Key"
  export appsec_slack_channel="Appsec team Slack channel to get notifications"
  export dojo_api_key="DefectDojo API key"
  export dojo_host_url="DefectDojo host link"
  export jira_api_token="Jira API token"
  export jira_instance="Jira host link"
  export jira_username="Jira username"
  export jtra_slack_channel="Slack channel to receive notifications for High risk Jira ticket"
  export slack_token="DefectDojo API key"
```

Run 
``` 
cd src
python3 app.py
```
SDARQ backend will run in the port 8080 of your localhost


### Questions
If you have questions, please reach out to AppSec team `appsec@broadinstitute.org`. 
