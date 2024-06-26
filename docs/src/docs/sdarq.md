---
id: sdarq
title: Sdarq
---

A tool built by the Application Security Team at the DSP, Broad Institute.

Sdarq is a coordination platform to guide both developers and AppSec professionals through an SDLC and provide interfaces into various tools and bind them.

It allows product teams to be aware of all security-related and compliance-related requirements as early as possible, ideally before they have even written a single line of code and for better visibility and eventually better mitigation for any potential vulnerabilities that may exist in any service. By serving as a bridge on the partnership between the Appsec team and Product teams, SDARQ helps engineers develop secure services as part of Terra by generating actionable and specific security requirements based on the technical characteristics of the service being built.

SDARQ orchestrates different security tools and scanners owned by the DSP Appsec team. These tools include DefectDojo, CodeDx, CIS Scanner, ZAP Scanner.

![sdarq](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/img/sdarq_app.png)

## What does it offer?

### New Service/App Requirements

- Create a security checklist (recommendations) for dev teams
- Report to Slack
- Create tickets in Jira
- Create product in DefectDojo
- Scan GCP project if provided
- Create a new item at Security Controls

### CIS Scanner

- Assess security posture of GCP projects
- Automate scans and automates reports
- Report to Slack

### Service Scan

- Assess security posture of a service/endpoint
- Report to Slack
- Upload results to CodeDx (optional)
- Upload results to DefectDojo

### Jira Ticket Risk Assessment

- Assess security risk of dev’s actions to a service

### Service/product Security Controls

- List all security controls implemented for a service/product
- Add/edit/delete security controls for a service
- Weekly auto updates that check if services security controls have been updated for DAST & 3rd party dependecies scans
- Weekly reminders for AppSec team to take actions if security controls are missing for services

### Security Requests

- Send requests to AppSec team to build a threat model for your service.
- Send requests to AppSec team to run a security pentest against your service.


## Architecture

![architecture](https://broadinstitute.github.io/dsp-appsec-infrastructure-apps/img/sdarq.png)

