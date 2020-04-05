#!/usr/bin/env python3

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message
from hashlib import md5
from kubernetes.client import BatchV1Api, V1Job, V1ObjectMeta
from kubernetes.config import load_kube_config
import logging as log
from os import environ
from typing import Callable
import yaml


def render_job(name: str, subscription: str, spec: str, job_input: str) -> V1Job:
    metadata = V1ObjectMeta(name=name)
    spec = spec.format(JOB_INPUT=job_input)
    spec = yaml.safe_load(spec)
    return V1Job(
        api_version='batch/v1',
        kind='Job',
        metadata=metadata,
        spec=spec,
    )


def callback(batch_v1: BatchV1Api, namespace: str, spec: str) -> Callable[[Message], None]:
    def cb(m: Message):
        try:
            job_name = md5(m.message_id.encode('utf-8')).hexdigest()
            job_input = m.data.decode('utf-8')
            log.info(f'Submitting job {job_name} with input "{job_input}"')

            job = render_job(job_name, spec, job_input)
            batch_v1.create_namespaced_job(namespace, job)
            log.info(f'Submitted job {job_name}')
        except Exception:
            log.exception('PubSub subscriber callback')
        m.ack()
    return cb


def listen(subscription: str, batch_v1: BatchV1Api, namespace: str, spec: str) -> None:
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        cb = callback(batch_v1, namespace, spec)
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


def main():
    namespace = environ['NAMESPACE']
    subscription = environ['SUBSCRIPTION']
    spec_path = environ['SPEC_PATH']
    log_level = environ.get('LOG_LEVEL', 'INFO')

    log.basicConfig(level=log_level)

    spec = load_job_spec(spec_path)

    load_kube_config()
    batch_v1 = BatchV1Api()

    listen(subscription, batch_v1, namespace, spec)


if __name__ == '__main__':
    main()
