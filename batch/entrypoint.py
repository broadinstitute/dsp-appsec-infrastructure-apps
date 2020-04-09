#!/usr/bin/env python3
"""
Listens to a PubSub subscription
and submits a Kubernetes Job for each message.
"""

import logging as log

from copy import deepcopy
from hashlib import md5
from os import environ
from threading import Thread
from typing import Callable, Dict

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message

from kubernetes.client import BatchV1Api, V1Job, V1JobSpec, V1ObjectMeta, rest
from kubernetes.config import config_exception, load_kube_config, load_incluster_config
from kubernetes.watch import Watch

import yaml

JobInputs = Dict[str, str]


def get_job(subscription: str,
            name: str, spec: V1JobSpec, job_inputs: JobInputs) -> V1Job:
    """
    Constructs Job request with spec and metadata.

    Spec template annotations are set/updated with `job_inputs`.
    """
    spec = deepcopy(spec)
    anno = spec['template'].setdefault('annotations', {})
    anno.update(job_inputs)

    return V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=V1ObjectMeta(
            name=name,
            labels={
                'subscription': subscription,
            },
        ),
        spec=spec,
    )


def get_pubsub_callback(subscription: str,
                        namespace: str, job_spec: V1JobSpec) -> Callable[[Message], None]:
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
            job_name = subscription + '-' + \
                md5(msg.message_id.encode('utf-8')).hexdigest()
            job_inputs = msg.attributes
            log.info('Submitting job %s with input(s) %s',
                     job_name, job_inputs)

            job = get_job(subscription, job_name, job_spec, job_inputs)
            get_batch_api().create_namespaced_job(namespace, job)
            log.info('Submitted job %s', job_name)

        except (UnicodeError, rest.ApiException):
            log.exception('PubSub subscriber callback')

        msg.ack()
    return callback


def listen_pubsub(project_id: str, subscription: str, namespace: str, job_spec: V1JobSpec) -> None:
    """
    Subscribes callback function to messages in the PubSub Subscription.

    Waits indefinitely until subscription produces an error.
    """
    with pubsub_v1.SubscriberClient() as subscriber:
        # https://github.com/googleapis/python-pubsub/issues/67
        subscription_path = f'projects/{project_id}/subscriptions/{subscription}'
        callback = get_pubsub_callback(subscription, namespace, job_spec)
        streaming_pull = subscriber.subscribe(subscription_path, callback)
        log.info('Listening to subscription %s', subscription)
        try:
            streaming_pull.result()
        except (TimeoutError, Exception) as err:
            streaming_pull.cancel()
            raise err


def load_job_spec(spec_path: str) -> V1JobSpec:
    """
    Reads job spec from `spec_path` into a YAML object.
    """
    with open(spec_path) as spec:
        return yaml.safe_load(spec)


def get_batch_api() -> BatchV1Api:
    """
    Attempts to load Kubernetes config from kube_config,
    or otherwise loads it from in-cluster config (when run as a Pod).

    Returns the initialized BatchV1Api object.
    """
    try:
        load_kube_config()
    except config_exception.ConfigException:
        load_incluster_config()
    return BatchV1Api()


def is_job_terminated(job: V1Job) -> bool:
    """
    Detects if a Job was terminated.
    """
    conds = job.status.conditions
    if not conds:
        return False
    for cond in conds:
        if cond.type in ('Complete', 'Failed') and cond.status == 'True':
            return True
    return False


def cleanup(subscription: str, namespace: str) -> None:
    """
    Watches for events from `list_namespaced_job` API call,
    and deletes terminated Jobs.

    This function would not normally be needed if `ttlSecondsAfterFinished` worked.
    However, that feature is currently hidden behind an `alpha` flag,
    so we do the cleanup explicitly here instead.
    """
    events = Watch().stream(
        get_batch_api().list_namespaced_job,
        namespace,
        label_selector=f'subscription={subscription}',
    )
    for event in events:
        if event['type'] == 'DELETED':
            continue
        job: V1Job = event['object']
        if is_job_terminated(job):
            meta = job.metadata
            get_batch_api().delete_namespaced_job(
                meta.name, meta.namespace, propagation_policy='Background',
            )
            log.info('Deleted job %s', meta.name)


def schedule_cleanup(subscription: str, namespace: str) -> None:
    """
    Schedules :func:`cleanup` to run on a background thread.
    """
    Thread(target=cleanup, args=(subscription, namespace)).start()


def main() -> None:
    """
    Parses inputs from environmental variables.
    Configures basic logging.
    Schedules cleanup of terminated Jobs.
    Loads job spec from `SPEC_PATH`.
    Sets up listener for the PubSub subscription.
    """

    project_id = environ['PROJECT_ID']
    subscription = environ['SUBSCRIPTION']
    namespace = environ['NAMESPACE']
    spec_path = environ['SPEC_PATH']
    log_level = environ.get('LOG_LEVEL', 'INFO')

    log.basicConfig(level=log_level)

    schedule_cleanup(subscription, namespace)
    job_spec = load_job_spec(spec_path)
    listen_pubsub(project_id, subscription, namespace, job_spec)


if __name__ == '__main__':
    main()
