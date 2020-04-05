#!/usr/bin/env python3

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message
from hashlib import md5
from kubernetes.client import BatchV1Api, V1Job
from kubernetes.config import load_kube_config
import logging as log
from os import environ, path
import re
from typing import Callable
import yaml


def render_job(tmpl: str, job_id: str, job_input: str) -> V1Job:
    environ['JOB_ID'] = job_id
    environ['JOB_INPUT'] = job_input

    tmpl = path.expandvars(tmpl)
    undef = re.findall(r'\${[^{]+}', tmpl)
    if undef:
        raise ValueError(
            f'Undefined variable(s) in {tmpl}: {undef}'
        )
    return yaml.safe_load(tmpl)


def callback(batch_v1: BatchV1Api, namespace: str, tmpl: str) -> Callable[[Message], None]:
    def cb(m: Message):
        try:
            job_id = md5(m.message_id.encode('utf-8')).hexdigest()
            job_input = m.data.decode('utf-8')
            log.info(f'Submitting job {job_id} with input "{job_input}"')

            job = render_job(tmpl, job_id, job_input)
            batch_v1.create_namespaced_job(namespace, job)
            log.info(f'Submitted job {job_id}')
        except Exception:
            log.exception('PubSub subscriber callback')
        m.ack()
    return cb


def listen(subscription: str, batch_v1: BatchV1Api, namespace: str, tmpl: str) -> None:
    subscriber = pubsub_v1.SubscriberClient()
    with subscriber:
        cb = callback(batch_v1, namespace, tmpl)
        streaming_pull = subscriber.subscribe(subscription, cb)
        log.info(f'Listening to subscription {subscription}')
        try:
            streaming_pull.result()
        except Exception as e:
            streaming_pull.cancel()
            raise e


def load_job_template(tmpl_path: str) -> str:
    with open(tmpl_path) as f:
        return f.read()


def main():
    subscription = environ['SUBSCRIPTION']
    namespace = environ['NAMESPACE']
    tmpl_path = environ['TEMPLATE_PATH']
    log_level = environ.get('LOG_LEVEL', 'INFO')

    log.basicConfig(level=log_level)

    tmpl = load_job_template(tmpl_path)

    load_kube_config()
    batch_v1 = BatchV1Api()

    listen(subscription, batch_v1, namespace, tmpl)


if __name__ == '__main__':
    main()
