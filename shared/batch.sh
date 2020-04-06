#!/usr/bin/env bash

set -euo pipefail

###
# This script deploys batch Job dispatcher container,
# which listens to a PubSub topic for job inputs
# and submits Kubernetes Jobs with those.
#
# Input variables:
#   PROJECT_ID - GCP project ID
#   NAMESPACE - namespace for deployment
#   BATCH_DISPATCHER_IMAGE - Docker image for the dispatcher
#   JOB_CREATOR_ROLE - ClusterRole for creating Jobs
#   JOB_TOPIC - PubSub topic name to be created by this script
#   JOB_CONFIG_MAP - name of the ConfigMap storing the Job spec
#
# JOB_CONFIG_MAP must store Job spec as a string under 'spec' key.
#
# Job spec must contain a literal {JOB_INPUT},
# which will be replaced with the contents
# of an incoming PubSub message,
# and it is up to the Job how to interpret it
# (for example, you can pass it as
# a command-line arg, or an env variable).
#

export JOB_SUBSCRIPTION="${JOB_TOPIC}"
export JOB_DEPLOYMENT="${JOB_TOPIC}-dispatcher"
export JOB_CONFIG_VOLUME="job-config"
export JOB_CONFIG_MOUNT_PATH="/job"
export JOB_SPEC_KEY="spec"

export SERVICE="${JOB_DEPLOYMENT}"
export SERVICE_ACCOUNT="${SERVICE}"

./kube-apply.py "service-account.yaml" "batch.yaml"
