---
id: cis_scan
title: CIS Scan Automation
---

CIS scanner is an internal scanner developed by DSP AppSec team to assess the security posture of our GCP projects.
This scanner scans a GCP project with Inspec GCP CIS Benchmark. Profiles listed below:
- inspec-gcp-cis-benchmark
- inspec-gke-cis-gcp
- inspec-gke-cis-k8s

CIS scanner runs:
- independent (weekly scanner)
- on-demand (integrated to Sdarq)

## Managing the list of scanned GCP projects

The list of GCP projects scanned by the weekly scanner is **not** hardcoded in the repo. It lives in the Cloud Build **trigger** as the substitution variable `_CIS_PROD_PROJECTS`.

Data flow:
- `cloudbuild.yaml` declares `_CIS_PROD_PROJECTS` (blank by default, set on the trigger) and passes it into the `cis` deploy step as the env var `CIS_PROD_PROJECTS`.
- `cis/deploy.sh` propagates it to the Kubernetes CronJob.
- `cis/scanweekly.py` reads `CIS_PROD_PROJECTS` and splits it on `,` to build the list of projects to scan.

### Show the current list

First find the trigger, then read its substitution:

```bash
# list triggers to get the name/id
gcloud builds triggers list --region=us-east1 \
  --format='table(name,id,github.name)'

# show just the CIS projects substitution for a given trigger
gcloud builds triggers describe TRIGGER_NAME --region=us-east1 \
  --format='value(substitutions._CIS_PROD_PROJECTS)'
```

(Drop `--region` / use `--region=global` if the trigger is global.)

### Modify the list

```bash
gcloud builds triggers update github TRIGGER_NAME --region=us-east1 \
  --update-substitutions=_CIS_PROD_PROJECTS='proj-a,proj-b,proj-c'
```

Notes:
- `--update-substitutions` merges/overwrites just that key; other substitutions are left alone.
- The value must be comma-separated with **no spaces** — the code does a plain `.split(",")`, so a stray space would produce an invalid project id (e.g. `" proj-b"`) and the publish would fail.
- Use the trigger subcommand matching its type (`github`, `cloud-source-repositories`, etc.). If unsure, run `gcloud builds triggers update --help`.
- The new value only takes effect on the next build/deploy of the `cis` step (which re-applies the CronJob env). To scan immediately with the new list, re-run the trigger:

  ```bash
  gcloud builds triggers run TRIGGER_NAME --region=us-east1 --branch=master
  ```
