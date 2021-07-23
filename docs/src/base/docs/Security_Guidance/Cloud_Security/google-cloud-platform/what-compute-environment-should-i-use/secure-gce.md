---
description: Set up a secure compute engine instance.
---

# Secure GCE

When launching 

### 1. Use only [CIS hardened images](https://console.cloud.google.com/marketplace/browse?q=CIS) or Shielded VM images for your boot disk.

![Click &quot;Change&quot; image under Boot Disk, and check the box to see Shielded VMs.](/img/shielded_vm.png)

### 2. Use a managed network with a subnet.

Scroll to the bottom and click "Management, security, disks, networking, sole tenancy". Select the "Networking" tab. Use a Network tag to set the firewall rules for the instance.

![Choose a network tag to determine the firewall rules for this instance.](/img/gce-network.png)

### 3. Use Google IAM for SSH Access

If a user needs access to a Compute Engine instance, add them to the subnet's IAM policy with a role with the minimum necessary permissions.

`gcloud compute networks subnets add-iam-policy-binding ([SUBNETWORK] : --region=[REGION]) --member='user:[USER]@broadinstitute.org' --role='roles/compute.instanceAdmin.v1'`

#### Additional Reading for Compute Engine IAM

* [https://cloud.google.com/compute/docs/instances/managing-instance-access](https://cloud.google.com/compute/docs/instances/managing-instance-access)
* [https://cloud.google.com/compute/docs/access/granting-access-to-resources](https://cloud.google.com/compute/docs/access/granting-access-to-resources)

## Production Data Requirements

### 1. Make sure OS automatic updates are on.

* Centos - [https://serversforhackers.com/c/automatic-security-updates-centos](https://serversforhackers.com/c/automatic-security-updates-centos) 
* Ubuntu - [https://help.ubuntu.com/lts/serverguide/automatic-updates.h](https://help.ubuntu.com/lts/serverguide/automatic-updates.html.en)

### 2. Set up logging on your VM.

VM logs should use StackDriver and SIEM. See [https://cloud.google.com/logging/docs/agent/installation](https://cloud.google.com/logging/docs/agent/installation) for installation instructions.

1. System logs are picked up by default.
2. Application logs should write to a file that gets picked up by StackDriver.
3. Contact BITS about having logs go to a SIEM

#### Additional Reading

* [https://cloud.google.com/logging/docs/agent/configuration](https://cloud.google.com/logging/docs/agent/configuration)

