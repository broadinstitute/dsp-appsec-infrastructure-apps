---
id: kubernetes-cluster
title: Kubernetes Cluster Architecture
sidebar_label: AppSec Infrastructure
---

Check the [documentation](https://dsp-security.broadinstitute.org) for how we do AppSec. 

## Deployment

All apps are deployed via Cloud Build, as defined in [cloudbuild.yaml](cloudbuild.yaml).


### Shared resources

### Terraform
First, it sets up some common infrastructure:

1.  Using [Terraform templates](terraform), it deploys a _regional_ GKE cluster with

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

2.  Then, it installs GKE Config Connector (via [shared/cnrm.sh](shared/cnrm.sh) script)
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
    and the following GCP resources in it ([shared/global.yaml](shared/global.yaml)):

    - Cloud Armor [Security Policy](https://cloud.google.com/armor/docs/security-policy-concepts),
      which firewalls all Ingress endpoints to the Broad CIDRs.

    - [Cloud DNS Managed Zone](https://cloud.google.com/dns/zones)
      for `dsp-appsec.broadinstitute.org.`

    - [GCE Resource Policy](https://cloud.google.com/compute/docs/disks/scheduled-snapshots)
      for disk snapshots (see below).




## Apps

Next, Cloud Build applies both app-specific and some [shared](shared)
Kubernetes _templates_ to deploy each app.

Some apps require patches to work properly with Docker/Kubernetes,
so we build patched images and push them to GCR along the way.
We use [Kaniko](https://github.com/GoogleContainerTools/kaniko) Docker builder
to speed up the builds through caching.

Each Kubernetes deployment is done via an associated `deploy.sh` script
(e.g. one for [CodeDx](codedx/deploy.sh)).
A quick overview of what that script should do:

1.  Create a [Kubernetes namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) for the app.
    Namespaces provide mainly logical/deployment separation,
    but also some security boundaries for the apps (notably, while
    Network Policy is not enabled by default, it can be
    [configured](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
    to accept internal cluster traffic only from specific namespaces).

    Namespaces are also very convenient for avoiding "spillover" of
    resources between the apps, as one namespace can be created/destroyed
    completely without affecting any others. This is particularly useful
    during the development of each app.

    We use [shared/kube-apply.py](shared/kube-apply.py) script to replace
    `PROJECT_ID` and `NAMESPACE` environment variables
    in [namespace.yaml](shared/namespace.yaml) template with app-specific values,
    and then apply it. This pattern is used throughout
    other resource deployments later as well.

2.  Generate Kubernetes secret(s) used by the app, unless they're "external" (e.g. a Slack token).
    This is done via [shared/gen-secret.sh](shared/gen-secret.sh) script, which currently uses
    `/dev/urandom` to generate a random sequence of alphanumeric characters. However,
    it may be better to use a crypto library in the future instead.

    The secrets are generated only once, when they don't exist yet. Otherwise,
    the script doesn't overwrite them. This provides a simple way to rotate the secrets,
    should we need that, by just removing them in Kubernetes and re-running the latest
    build in Cloud Build.

    For the manually created secrets, we'll provide a sample template to deploy them
    from your local shell.

3.  Set up a Kubernetes volume for the app, if it stores some of its state on disk
    (e.g. DefectDojo and CodeDx).

    This is done via [shared/volume.sh](shared/volume.sh) script that
    - declares a regional GCE disk (which can be accessed from any of the 2 zones
      in the cluster, while also providing regional replication)
    - sets up daily snapshots of disk content for disaster recovery
    - waits for the disk to be created on GCE
    - sets up Kubernetes
      [PersistentVolume and PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/),
      where the latter can be used to associate the volume with a Pod.

4.  If the app needs access to GCP services (e.g. Cloud SQL), apply
    [shared/service-account.yaml](shared/service-account.yaml) template to:
    - create a Kubernetes Service Account (KSA) for its Pod
    - create a Google Service Account (GSA) that will have access to GCP resources
    - binds these 2 accounts via a Kubernetes annotation and `iam.workloadIdentityUser` role.

    Note that `service-account.yaml` is generic and _doesn't_ grant access to GCP resources,
    so after applying it, the actual role binding has to be done via an app-specific template
    (but at least, that step is simple).

5.  Apply the app-specific template,
    which creates either a Deployment (for stateless apps),
    or a StatefulSet (if the app uses disk).

    We also deploy any app-specific GCP resources (e.g. SQLInstance, SQLUser etc.)
    via Config Connector resource types, and create a role binding for the service account
    (if any in use), e.g. `roles/cloudsql.client` for Cloud SQL.

    Finally, it's recommended to set `runtimeClassName: gvisor` for the Pod,
    to enable GKE Sandbox around it. However, some apps (e.g. DefectDojo) may fail
    to work properly with it. In that case, the app can still be deployed without it, but
    will need an extra configuration snippet for `nodeSelector` and `tolerations`
    (e.g. see how this is done in [defectdojo/deployment.yaml](defectdojo/deployment.yaml)).

    For the next steps, this template should also expose
    a `containerPort` and a `readinessProbe`, both of which are used
    to reach the app http endpoint from Ingress and to mark it as healthy.

    Take a look, for example, at how all of this is done in
    [codedx/deployment.yaml](codedx/deployment.yaml).

6.  Call [shared/host.sh](shared/host.sh) script, which:
    - declares a global static IP for the service
    - waits for the IP to be created
    - sets up its DNS hostname record in the Managed Zone
    - waits for DNS propagation by repeated host resolution
    - deploys [GKE Managed Certificate](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs)
      for the hostname

7.  Finally, deploy [shared/ingress.yaml](shared/ingress.yaml), which sets up:

    - [Backend Config](https://cloud.google.com/kubernetes-engine/docs/concepts/backendconfig)
      for Cloud Armor

    - [Kubernetes Service](https://kubernetes.io/docs/concepts/services-networking/service/), which:
        - exposes internal port(s) to the load balancer
        - applies Backend Config to those
        - sets up container-native load balancing via a
          [Network Endpoint Group](https://cloud.google.com/kubernetes-engine/docs/how-to/standalone-neg)

    - [GKE Ingress](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress),
      which ties together all of the above using:
      - IP address binding
      - Disallowing raw HTTP (to keep only HTTPS)
      - Managed Certificate binding
      - DNS hostname mapping via Host header of the request
      - URL path mapping for each Service port

    Please note that `ingress.yaml` may need to be adjusted in an app-specific way
    (e.g. for Sdarq, which exposes multiple internal paths/ports,
    and could use Cloud DNS for Backend Config), in which case
    a customized copy of `ingress.yaml` would need to be referenced from `deploy.sh`.

## Questions
`appsec@broadinstitute.org`

