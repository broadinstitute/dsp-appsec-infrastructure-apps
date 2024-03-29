---
id: defectdojo_codedx
title: How we use DefectDojo & CodeDx
---

### CodeDx

CodeDX is a vulnerability management tool used by the AppSec team. Currently in this infrastructure it is used
to send ZAP scan results. 

CodeDx is Optional, since ZAP scan results can be uploaded to DefectDojo too. 

### DefectDojo

DefectDojo is used for many purposes and it is integrated with SDARQ and ZAP scans. 

- SDARQ: When a new service questionnaire is completed, it will trigger creation of a new project in DefectDojo with all data provided. 

- ZAP scans: Endpoints list to be scanned are found in endpoint list of ZAP scans. When scans results are generated they will be uploaded to a project in DefectDojo and project in Codedx. 

- Products in DefectDojo that have the tag `srcclr` and `zap`, they set automatically to green check (true) the security control for DAST and 3rd party dependencies scan for the associated product in the security controls in Sdarq