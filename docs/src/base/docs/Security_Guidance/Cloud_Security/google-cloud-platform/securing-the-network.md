---
description: 'Note: You should do this even if you’re not using GCE'
---

# Securing the Network

## Close SSH and RDP access

1. Disable the `default-allow-ssh` and `default-allow-rdp` firewall rules. This disables port tcp:22 and tcp:3389, which allow access to all VMs on the default network.
2. Make sure machines are deployed to a non-default network that does not include these rules.

Example:

`gcloud compute firewall-rules delete default-allow-ssh default-allow-rdp --project [PROJECT-NAME]`

See Google Cloud's [Firewall documentation](https://cloud.google.com/vpc/docs/using-firewalls) for reference.

## OPTIONAL: Create a new managed network and subnet

### 1. Delete the Network

Delete the default network.

`gcloud compute networks delete default`

### 2. Create a managed network and subnet - allow only Broad Networks to access

Create a network:

`gcloud compute networks create [NETWORK-NAME]`

Create a subnet:

`gcloud compute networks subnets create [SUBNET-NAME] --network=[NETWORK-NAME] --enable-flow-logs --range=10.100.1.0/24`

We recommend using the `[NETWORK-NAME]-subnet` format for your subnet name. You may also want to change the range for your subnet, but please talk to BITs when creating a unique range.

### 3. Create Firewall Rules

Firewall rules refer to either incoming(ingress) or outgoing(egress) traffic. You can target certain types of traffic based on its protocol, ports, sources, and destinations.

* Be REALLY mindful when creating new rules. 
* If you want to alter the range of ports, [update the current rule](https://cloud.google.com/vpc/docs/using-firewalls#updating_firewall_rules) rather than create a new one. 
* DO NOT USE the `broad-allow` tag when creating a new rule. 
* It is recommended to use the network in the rule's name.

```text
gcloud compute firewall-rules create NAME \
    [--network NETWORK; default="default"] \
    [--priority PRIORITY;default=1000] \
    [--direction (ingress|egress|in|out); default="ingress"] \
    [--action (deny | allow )] \
    [--target-tags TAG,TAG,...] \
    [--target-service-accounts=IAM Service Account,IAM Service Account,...] \
    [--source-ranges CIDR-RANGE,CIDR-RANGE...] \
    [--source-tags TAG,TAG,...] \
    [--source-service-accounts=IAM Service Account,IAM Service Account,...] \
    [--destination-ranges CIDR-RANGE,CIDR-RANGE...] \
    [--rules (PROTOCOL[:PORT[-PORT]],[PROTOCOL[:PORT[-PORT]],...]] | all ) \
    [--disabled | --no-disabled]
    [--enable-logging | --no-enable-logging]       
```

The following example will enable all Broad users on VPN or at a Broad office to contact all machines in the network but be blocked to the rest of the world.

```text
gcloud --project --account compute firewall-rules create [RULES-NAME] \
    --allow=tcp \ # could also use tcp:0-60000
    --target-tags broad-allow \ 
    --network=[NETWORK-NAME] \
    --source-ranges=69.173.112.0/21,69.173.127.232/29,69.173.127.128/26,69.173.127.0/25,69.173.127.240/28,69.173.127.224/30,69.173.127.230/31,69.173.120.0/22,69.173.127.228/32,69.173.126.0/24,69.173.96.0/20,69.173.64.0/19,69.173.127.192/27,69.173.124.0/23 \
    --enable-logging
```

Look at the [docs for Firewall rules](https://cloud.google.com/vpc/docs/using-firewalls#creating_firewall_rules) to see more on how to open your machines to the outside world or how to **narrow** to a set of machines(“targets”).

