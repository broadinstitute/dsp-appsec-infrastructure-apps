---
description: Do not download service account keys.
---

# Service Account Keys

If an attacker can access your downloaded service account key, he can sign a JWT token and be granted an API access token. 

There is a way to avoid this and instead of downloading the service account key, use

####  —impersonate-service-account flag

```text
gcloud --impersonate-service-account=k8s@project.iam.gserviceaccount.com container clusters get-credentials my-cluster
```

It allows this command to use a service account without actually having the key, but by using service account impersonation.

If you are running multiple commands with same SA, use these commands before: 

```text
gcloud config set auth/impersonate_service_account \
  k8s@project.iam.gserviceaccount.com
gcloud container clusters get-credentials my-cluster

# Other gcloud commands :)

```

If you are switching to a different SA, write a simple bash script to switch between different SA:

```text
#!/bin/bash
IMPERSONATE='gcloud config set auth/impersonate_service_account'
impersonate() {
 sa=$1
 echo "Impersonating $sa"
 $IMPERSONATE $sa
}
case $1 in
gke)
 impersonate k8s@project.iam.gserviceaccount.com
 ;;
admin)
 impersonate admin@other-project.iam.gserviceaccount.com
 ;;
clear)
 gcloud config unset auth/impersonate_service_account
 ;;
*)
 echo "Usage: Updates impersonated service account"
 echo "  gsa [gke|admin|clear]"
esac
```

## Terraform

Google terraform provider supports directly passing an OAuth2 token as an environment variable. All you have to do is get this token and tell Terraform about it.  This token will live in the env for just one hour and will be useless after that. 

```text
export GOOGLE_OAUTH_ACCESS_TOKEN=$(gcloud auth print-access-token)
terraform apply
```

## Attribution and Logging

In Cloud Logging every API call executed by a SA that has been impersonated has the following structure. 

```text
{
  "principalEmail": "k8s@project.iam.gserviceaccount.com",
  "serviceAccountDelegationInfo": [
    {
      "firstPartyPrincipal": {
        "principalEmail": "harry.potter@example.com"
      }
    }
  ]    
}
```

By enabling Data Access Logs, you can get more detail about every API call that harry.potter@example.com made while impersonating.

