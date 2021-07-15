---
id: kubernetes-cluster
title: Kubernetes Cluster Architecture
sidebar_label: AppSec Infrastructure
---
# Infrastructure

## Deployment

All apps are deployed via Cloud Build, as defined in cloudbuild.yaml.

### Shared resources

### Terraform
First, it sets up some common infrastructure:

1.  Using Terraform templates, it deploys a _regional_ GKE cluster with

    - a dedicated VPC network/subnetwork in `us-east1` region

    - VPC-native networking with
      [alias IPs](https://cloud.google.com/kubernetes-engine/docs/how-to/alias-ips),
      to optimize pod communication and provide some security benefits

    - a minimal-privilege GKE node service account
      with access to Stackdriver logging/monitoring
      and Google Container Registry

    - `system` and `sandbox` node pools,
      spread across 2 availability zones in the region

    - [GKE Sandbox](https://cloud.google.com/kubernetes-engine/sandbox)
      enabled for `sandbox` pool,
      which will be used for app deployments
      (with additional configuration for the pods, see below).

    - [Container-Optimized OS with `containerd` runtime](https://cloud.google.com/kubernetes-engine/docs/concepts/using-containerd)
      image for the nodes (this is required by GKE Sandbox,
      but we also use it for "system" nodes, to minimize Docker exposure surface)

    - [Shielded VMs](https://cloud.google.com/security/shielded-cloud/shielded-vm)
      for all nodes

    - [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) for minimal-privilege app deployments

    - [Network Policy](https://cloud.google.com/kubernetes-engine/docs/tutorials/network-policy) cluster add-on for future Pod deployments

    - [Cluster Autoscaler](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler)
      for `sandbox` pool, to gradually grow the number of nodes as more workloads are deployed to them

    - _Regular_ [release channel](https://cloud.google.com/kubernetes-engine/docs/concepts/release-channels) for cluster/node upgrades


### GKE Config Connector

2.  Then, it installs GKE Config Connector (via shared/cnrm.sh script)
    into `system` pool.

    [Config Connector](https://cloud.google.com/config-connector/docs/overview)
    is a new GKE cluster add-on that enables declarative
    deployment of GCP resources directly from Kubernetes templates.

    This is highly convient, as we can deploy a Pod, an associated minimal privilege Service Account,
    and related GCP resources (e.g. CloudSQL instances) within a single template.

    Notice that Config Connector itself needs access to create these GCP resources,
    and as such is assigned a highly-privileged Service Account with the
    required permissions via a custom IAM role in Terraform. However,
    we schedule its pods into `system` node pool, so it is physically separated
    from all "third-party apps" in the cluster.

    If this becomes a big concern, it's possible to deploy Config Connector
    onto a separate project/cluster altogether,
    and then managing "target project" resources from there
    (or alternatively, we could use Terraform to deploy these GCP resources,
    but that introduces its own complexities).

    However, even the current setup may provide sufficient isolation, and is
    still better than the regular "Default Compute Engine Service Account Identity"
    typically used for GKE nodes and pods, since
    the workloads (apps) are now isolated by multiple layers
    (workload identity, containerization, GKE Sandbox where possible,
    physical nodes, and Network Policies in the future).

    It's also possible to protect GCP resources from deletion when
    an associated Config Connector resource is removed. This can be done
    via `cnrm.cloud.google.com/deletion-policy: abandon` annotation for the resource.
    We use it for such resources as `SQLInstance/Database/User`,
    `ComputeAddress`, `DNSManagedZone`, `ComputeDisk`, and `ComputeResourcePolicy`,
    as those generally need to "survive" any cluster/app re-deployments.

    Since Config Connector relies on the project-global names of such resources,
    they are automatically "acquired" by it on re-deployment. This allows us
    to safely delete an entire namespace or even the cluster, and
    re-create it later on, so the cluster/namespaces can be treated as "dispensable"
    resources that can be completely and easily reproduced via Cloud Build, when needed.

    [Here](https://cloud.google.com/config-connector/docs/reference/resources)
    is a comprehensive list of all possible GCP resources available via Config Connector.


### Global Namespace in GKE

3.  Finally, using Config Connector we set up `global` namespace (see below)
    and the following GCP resources in it (shared/global.yaml):

    - Cloud Armor [Security Policy](https://cloud.google.com/armor/docs/security-policy-concepts),
      which firewalls all Ingress endpoints to the Broad CIDRs.

    - [Cloud DNS Managed Zone](https://cloud.google.com/dns/zones)
      for `dsp-appsec.broadinstitute.org.`

    - [GCE Resource Policy](https://cloud.google.com/compute/docs/disks/scheduled-snapshots)
      for disk snapshots (see below).