---
id: zap_scan
title: Zap Scan Automation
---

Automated Zap scanning developed mainly for compliance purposes.
Zap scans uses the GKE job-dispatcher pattern to run weekly and monthly scans. A weekly and monthly cron job fetches a list of endpoints and scan-types from DefectDojo and sends a message with details about the endpoint and the scan-type to the job dispatcher. The job dispatcher then runs two containers - one that contains the headless-zap daemon and one that includes a python script to communicate with the zap instance and upload the results to DefectDojo product, send a slack message, and any other tasks that must be completed outside of the zap scan itself.


Defect Dojo is the single source of truth for zap scans. List of endpoints found here: https://defectdojo-host.com/endpoint

Each endpoint to be scanned must include a tag with the format 
- "engagement_id:[PRODUCT_ID]” Defectdojo product id where zap scan will upload the results.  
- “scan:[SCAN-TYPE]” the endpoint must also include a tag for each scan to be run on the endpoint in the form of `baseline`, `api`, `auth`, `ui`.
- “slack:[#SLACK-CHANNEL]” a tag specifying a slack channel for notifications is also included with each endpoint in the form .


Scan types:
- Baseline Scans - Spidering and Passive scans
- Auth Scans - Spidering and Passive scans but authenticate every 30 minutes by fetching a GCP OAuth token and using Zap’s Replacer tool
- API Scan - Imports an OpenAPI file (via URL) before running an auth scan
- UI Scan - Auth scan + Active Scan


ZAP scanner runs:
- independent (weekly & monthly scanner)
- on-demand (integrated to Sdarq)
