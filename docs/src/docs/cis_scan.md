---
id: cis_scan
title: CIS Scan Automation
---


CIS scanner is an internal scanner developed by AppSec team to assess the security posture of our GCP projects.
This scanner scans a GCP project with Inspec GCP CIS Benchmark. Profiles listed below:
- inspec-gcp-cis-benchmark
- inspec-gke-cis-gcp
- inspec-gke-cis-k8s

CIS scanner runs:
- independent (weekly scanner)
- on-demand (integrated to Sdarq)
