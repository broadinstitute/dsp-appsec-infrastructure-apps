#!/usr/bin/env python3

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message
from hashlib import md5
from kubernetes.client import BatchV1Api, V1Job, V1ObjectMeta
from kubernetes.config import load_kube_config, load_incluster_config
from kubernetes.watch import Watch
import logging as log
from os import environ
from threading import Thread
from typing import Callable
import yaml


def render_job(subscription: str, job_name: str, job_spec: str, job_input: str) -> V1Job:
    spec = job_spec.format(JOB_INPUT=job_input)
    spec = yaml.safe_load(spec)

    metadata = V1ObjectMeta(
        name=job_name,
        labels={
            'subscription': subscription,
        },
    )

    return V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=metadata,
        spec=spec,
    )


def callback(subscription: str, namespace: str, job_spec: str) -> Callable[[Message], None]:
    def cb(m: Message):
        try:
            job_name = subscription.split('/')[-1] + '-' + \
                md5(m.message_id.encode('utf-8')).hexdigest()
            job_input = m.data.decode('utf-8')
            log.info(f'Submitting job {job_name} with input "{job_input}"')

            job = render_job(subscription, job_name, job_spec, job_input)
            get_batch_v1().create_namespaced_job(namespace, job)
            log.info(f'Submitted job {job_name}')
        except Exception:
            log.exception('PubSub subscriber callback')
        m.ack()
    return cb


def listen(subscription: str, namespace: str, job_spec: str) -> None:
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        cb = callback(subscription, namespace, job_spec)
        streaming_pull = subscriber.subscribe(subscription, cb)
        log.info(f'Listening to subscription {subscription}')
        try:
            streaming_pull.result()
        except Exception as e:
            streaming_pull.cancel()
            raise e


def load_job_spec(spec_path: str) -> str:
    with open(spec_path) as f:
        return f.read()


def get_batch_v1() -> BatchV1Api:
    try:
        load_kube_config()
    except:
        load_incluster_config()
    return BatchV1Api()


def cleanup(subscription: str, namespace: str):
    for event in Watch().stream(
        get_batch_v1().list_namespaced_job,
        namespace,
        label_selector=f'subscription={subscription}',
    ):
        print('Event', event)


def schedule_cleanup(namespace: str):
    Thread(target=cleanup, args=namespace).start()


def main():
    namespace = environ['NAMESPACE']
    subscription = environ['SUBSCRIPTION']
    spec_path = environ['SPEC_PATH']
    log_level = environ.get('LOG_LEVEL', 'INFO')

    log.basicConfig(level=log_level)

    schedule_cleanup()
    job_spec = load_job_spec(spec_path)
    listen(subscription, namespace, job_spec)


if __name__ == '__main__':
    main()
