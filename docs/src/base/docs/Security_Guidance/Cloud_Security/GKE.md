# Google Kubernetes Engine (GKE)

## Service Account credentials

GKE apps can access Service Account credentials(which are used to access other Google APIs and services) through:

1.(**best practice**) [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview#workload_identity_recommended), if configured for the cluster and Pods.
2.(_deprecated_) Default or custom [Node Service Account](https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview#node_service_account).
3.(discouraged) [Service Account Keys](https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview#service_account_json_key). 

\(3) is still being used in many examples from Google documentation, however it's not advisable, mainly because long-term credentials should be rotated on a regular basis, and it can be hard to configure that, while simpler alternatives(1 and 2) exist.

\(2) and(1) allow for Service Account credentials to be discovered _**automatically**_ by Google client libraries, i.e. it's not necessary to "point" your app to a particular key location like in method(3). Just initialize [Google API SDK](https://cloud.google.com/apis/docs/cloud-client-libraries) for your language of choice, and the credentials will be "picked up" from the environment. 

\(2) is simple, however in an environment with _multiple_ apps per cluster, it leads to over-granting of permissions for various apps and unnecessary sharing of permissions between them.

\(1) is the new Google-recommended best practice, and is fairly straightforward to configure still. Please follow [this guide](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) on how to configure it.

### SSL certificates

GKE apps may present HTTPS endpoints using SSL certificates with:

1.(**best practice**) [Google-managed SSL certificates](https://cloud.google.com/kubernetes-engine/docs/how-to/managed-certs).
2.(**good practice**) [Cert-manager](https://cert-manager.io/docs/installation/kubernetes/).
3.(discouraged) [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/).

Method(3) is still used by many, but it is not great by the same arguments as for storing Service Account keys. Simpler methods exist(1 and 2).

\(2) can be used to _automatically_ provision and manage certs with Let's Encrypt(or other providers).

\(1) also _automatically_ provisions and manages certs, but is more integrated with the GKE Ingress and GCP ecosystem in general. In some _limited_ cases(e.g. wildcard certs) it offers fewer features than(2), but the support is growing, including the recently added ability to manage _multiple_ domain names per certificate.

### Other long-term credentials

* Database passwords
* Third-party API keys
* Credentials for other cloud providers

Storing these securely in GKE can be accomplished with:

1.(**best practice**) [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/), optionally with [application-level encryption](https://cloud.google.com/kubernetes-engine/docs/how-to/encrypting-secrets).
2.(**best practice**) [Secret Manager](https://cloud.google.com/secret-manager/docs/quickstart).
3.(**best practice**) [Hashicorp Vault](https://docs.dsp-devops.broadinstitute.org/framework-kernel-new-stack/framework-deployment#secrets).
4.(good practice) [Cloud KMS](https://cloud.google.com/kms/docs/quickstart).
5.(**best practice**) Federated access.

Options(1-3) are best, since they offer both a _dedicated_ secrets storage medium, and _auditability_ of _individual_ secret management/access([Kubernetes Secrets](https://cloud.google.com/kubernetes-engine/docs/how-to/audit-logging#enabling_data_access_logs), [Secret Manager](https://cloud.google.com/secret-manager/docs/audit-logging)). 

Kubernetes Secrets are slightly easier to use in the default configuration, as they don't require modification of the existing application code. However, enabling application-level encryption requires more work. Consider using Secret Manager, if you can modify the application code.

\(4) is also good as a general secrets _encryption_ solution, however it doesn't enable audit at the individual secret level(only at the _encryption key_ level). Use it when other options are not available.

\(5) may be possible for access to third-party APIs and other cloud providers, starting with only Google credentials. Setting them up depends on the particular service provider. [Here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html)'s an example for AWS.

### Short-term credentials

* Google OAuth, JWT and other temporary API tokens.
* Session cookies for web apps etc.

1.(**best practice**) Avoid handling of tokens explicitly in your code, unless your app authentication mechanism requires it. If possible, use [Cloud IAP](https://cloud.google.com/iap/docs/enabling-kubernetes-howto), [Istio/Envoy proxy](https://cloud.google.com/istio/docs/istio-on-gke/installing), [Cloud Endpoints](https://cloud.google.com/endpoints/docs/openapi/get-started-kubernetes-engine), [OpenIDC Proxy](https://github.com/broadinstitute/openidc-proxy), or another application-level authentication proxy that handles token validation for your API.
2.(**good practice**) Use well-established libraries(e.g. [Google libraries](https://developers.google.com/identity/sign-in/web/backend-auth), [JWT libraries](https://jwt.io/)) if you have to validate the tokens or otherwise process them on the backend. Additionally, clear variables used to store them as soon as you are finished with them, to avoid accidental leakage through the logs, third-party libraries etc.

Don't store temporary tokens on a file system, in a database, or another long-term storage medium. Doing so unnecessarily increases the risk of secret leakage, even if for a short time. Solutions(1) and(2) both allow managing these credentials for you.