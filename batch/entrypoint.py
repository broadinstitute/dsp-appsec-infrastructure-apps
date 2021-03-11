#!/usr/bin/env python3
"""
Listens to a PubSub subscription
and submits a Kubernetes Job for each message.
"""

import logging as log
import os
from copy import deepcopy
from hashlib import sha256
from os import environ
from threading import Thread
from typing import Callable, Dict

import yaml
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message
from kubernetes.client import ApiException, BatchV1Api, V1Job, V1ObjectMeta
from kubernetes.config import config_exception, load_incluster_config, load_kube_config
from kubernetes.watch import Watch

JobInputs = Dict[str, str]


def raise_from_thread(msg: str, *args):
    """
    Logs an exception raised in a thread and exits the program.
    When running inside Kubernetes, this forces the Pod to auto-restart,
    which is desirable to handle any transient errors.
    """
    log.exception(msg, *args)
    os._exit(1)  # pylint: disable=protected-access


def get_job(job: V1Job, name: str, inputs: JobInputs):
    """
    Returns a copy of the Job object with job `name`, where
    template annotations are set/updated with job `inputs`.
    """
    job = deepcopy(job)
    job.metadata.name = name
    anno = job.spec["template"]["metadata"]["annotations"]
    anno.update({**anno, **inputs})
    return job


def get_pubsub_callback(
    batch_api: BatchV1Api, subscription: str, namespace: str, job: V1Job
) -> Callable[[Message], None]:
    """
    Returns `callback` function to be called on every PubSub message
    """

    def callback(msg: Message):
        """
        Constructs `job_name` and `job_inputs` from
        `message_id` and attributes of a PubSub message.

        Submits rendered Job object to Kubernetes Batch API.
        """
        try:
            job_name = (
                subscription
                + "-"
                + sha256(msg.message_id.encode("utf-8")).hexdigest()[:16]
            )
            job_inputs: JobInputs = msg.attributes
            log.info("Submitting job %s with input(s) %s", job_name, job_inputs)

            new_job = get_job(job, job_name, job_inputs)
            batch_api.create_namespaced_job(namespace, new_job)
            log.info("Submitted job %s", job_name)

        except (UnicodeError, ApiException):
            raise_from_thread("Error in PubSub subscriber callback")

        msg.ack()

    return callback


def listen_pubsub(
    batch_api: BatchV1Api,
    project_id: str,
    subscription: str,
    namespace: str,
    job: V1Job,
):
    """
    Subscribes callback function to messages in the PubSub Subscription.

    Waits indefinitely until subscription produces an error.
    """
    with pubsub_v1.SubscriberClient() as subscriber:
        # https://github.com/googleapis/python-pubsub/issues/67
        subscription_path = f"projects/{project_id}/subscriptions/{subscription}"
        callback = get_pubsub_callback(batch_api, subscription, namespace, job)
        streaming_pull = subscriber.subscribe(subscription_path, callback)
        log.info("Listening to subscription %s", subscription)
        try:
            streaming_pull.result()
        except (TimeoutError, Exception) as err:
            streaming_pull.cancel()
            raise err


def load_job(subscription: str, spec_path: str):
    """
    Reads job spec from `spec_path` into a YAML object.

    Constructs a Job object with this spec.
    """
    with open(spec_path) as spec_file:
        spec = yaml.safe_load(spec_file)
        spec["template"].setdefault("metadata", {}).setdefault("annotations", {})

        return V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=V1ObjectMeta(
                labels={
                    "subscription": subscription,
                },
            ),
            spec=spec,
        )


def get_batch_api():
    """
    Attempts to load Kubernetes config from in-cluster config (when run as a Pod),
    or otherwise loads it from kube_config.

    Returns the initialized BatchV1Api object.
    """
    try:
        load_incluster_config()
    except config_exception.ConfigException:
        load_kube_config()
    return BatchV1Api()


def is_job_terminated(job: V1Job):
    """
    Detects if a Job was terminated.
    """
    conds = job.status.conditions
    if not conds:
        return False
    for cond in conds:
        if cond.type in ("Complete", "Failed") and cond.status == "True":
            return True
    return False


def cleanup(batch_api: BatchV1Api, subscription: str, namespace: str):
    """
    Watches for events from `list_namespaced_job` API call,
    and deletes terminated Jobs.

    This function would not normally be needed if `ttlSecondsAfterFinished` worked.
    However, that feature is currently hidden behind an `alpha` flag,
    so we do the cleanup explicitly here instead.
    """
    try:
        events = Watch().stream(
            batch_api.list_namespaced_job,
            namespace,
            label_selector=f"subscription={subscription}",
        )
        for event in events:
            if event["type"] == "DELETED":
                continue
            job: V1Job = event["object"]
            if is_job_terminated(job):
                meta = job.metadata
                batch_api.delete_namespaced_job(
                    meta.name,
                    meta.namespace,
                    propagation_policy="Background",
                )
                log.info("Deleted job %s", meta.name)
    except:  # pylint: disable=bare-except
        raise_from_thread("Error in Job cleanup")


def schedule_cleanup(batch_api: BatchV1Api, subscription: str, namespace: str):
    """
    Schedules :func:`cleanup` to run on a background thread.
    """
    Thread(target=cleanup, args=(batch_api, subscription, namespace)).start()


def main():
    """
    Parses inputs from environmental variables.
    Configures basic logging.
    Schedules cleanup of terminated Jobs.
    Loads job spec from `SPEC_PATH`.
    Sets up listener for the PubSub subscription.
    """

    project_id = environ["PROJECT_ID"]
    subscription = environ["SUBSCRIPTION"]
    namespace = environ["NAMESPACE"]
    spec_path = environ["SPEC_PATH"]
    log_level = environ.get("LOG_LEVEL", "INFO")

    log.basicConfig(level=log_level)

    batch_api = get_batch_api()
    schedule_cleanup(batch_api, subscription, namespace)
    job = load_job(subscription, spec_path)
    listen_pubsub(batch_api, project_id, subscription, namespace, job)


if __name__ == "__main__":
    main()
