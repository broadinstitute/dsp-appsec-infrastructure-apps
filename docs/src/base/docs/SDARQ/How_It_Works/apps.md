---
id: sdarq-apps
title: SDARQ Apps
sidebar_label: SDARQ Apps
---
# App Deployment

Next, Cloud Build applies both app-specific and some shared
Kubernetes _templates_ to deploy each app.

Some apps require patches to work properly with Docker/Kubernetes,
so we build patched images and push them to GCR along the way.
We use [Kaniko](https://github.com/GoogleContainerTools/kaniko) Docker builder
to speed up the builds through caching.

Each Kubernetes deployment is done via an associated `deploy.sh` script
(e.g. one for CodeDx.
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

    We use shared/kube-apply.py script to replace
    `PROJECT_ID` and `NAMESPACE` environment variables
    in namespace.yaml template with app-specific values,
    and then apply it. This pattern is used throughout
    other resource deployments later as well.

2.  Generate Kubernetes secret(s) used by the app, unless they're "external" (e.g. a Slack token).
    This is done via shared/gen-secret.sh script, which currently uses
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

    This is done via shared/volume.sh script that
    - declares a regional GCE disk (which can be accessed from any of the 2 zones
      in the cluster, while also providing regional replication)
    - sets up daily snapshots of disk content for disaster recovery
    - waits for the disk to be created on GCE
    - sets up Kubernetes
      [PersistentVolume and PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/),
      where the latter can be used to associate the volume with a Pod.

4.  If the app needs access to GCP services (e.g. Cloud SQL), apply
    shared/service-account.yaml template to:
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
    (e.g. see how this is done in defectdojo/deployment.yaml.

    For the next steps, this template should also expose
    a `containerPort` and a `readinessProbe`, both of which are used
    to reach the app http endpoint from Ingress and to mark it as healthy.

    Take a look, for example, at how all of this is done in
    codedx/deployment.yaml.

6.  Call shared/host.sh script, which:
    - declares a global static IP for the service
    - waits for the IP to be created
    - sets up its DNS hostname record in the Managed Zone
    - waits for DNS propagation by repeated host resolution
    - deploys [GKE Managed Certificate](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs)
      for the hostname

7.  Finally, deploy shared/ingress.yaml, which sets up:

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