#!/usr/bin/env python3

import argparse
import os

import requests
from google.cloud import pubsub_v1

futures = dict()


def get_defect_dojo_endpoints(url, key):
    endpoint = f'{url}/api/v2/endpoints/'
    token = f'Token {key}'

    headers = {'content-type': 'application/json',
               'Authorization': token}
    # set verify to False if ssl cert is self-signed
    r = requests.get(endpoint, headers=headers, verify=True)

    endpoints = r
    if r.status_code != 200:
        print(r.text)

    endpoints = r.json()["results"]

    return endpoints

def get_callback(future, data):
    """Handle publish failures."""
    def callback(future):
        try:
            print(future.result())
            futures.pop(data)
        except Exception:
            print("Please handle {} for {}.".format(future.exception(), data))

    return callback

def scan_endpoints(endpoints, gcp_project, topic_name, scans):
    """
    Scan multiple endpoints by publishing multiple
    messages to a Pub/Sub topic with an error handler.

    Args:
        List of endpoints to be scanned
        gcp project id
        pub sub topic

    Returns:
        None
    """
    message = ""
    message = message.encode("utf-8")

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(gcp_project, topic_name)

    for endpoint in endpoints:
        data = u"{}".format(endpoint)
        codedx_project = None
        slack_channel = ""
        bucket_name = ""
        for tag in endpoint["tags"]:
            # endpoints to scan will include tag codedx:CODEDX_PROJECT to identify project on codedx
            if "codedx" in tag:
                codedx_project = "".join(tag.split(":")[1:])
            if "slack" in tag:
                slack_channel = "".join(tag.split(":")[1:])
            if "bucket" in tag:
                bucket_name = "".join(tag.split(":")[1:])
        if codedx_project is not None:
            for scan_type in endpoint["tags"]:
                if scan_type in scans:
                    url = f"{endpoint['protocol']}://{endpoint['host']}{endpoint['path']}"
                    future = publisher.publish(
                        topic_path,
                        data=message,
                        CODEDX_PROJECT=codedx_project,
                        URL=url,
                        SCAN_TYPE=scan_type,
                        SLACK_CHANNEL=slack_channel,
                        BUCKET_NAME=bucket_name
                    )

                    futures[data] = future
                    # Publish failures shall be handled in the callback function.
                    future.add_done_callback(get_callback(future, data))


def main():
    defect_dojo_url = os.getenv('DEFECT_DOJO_URL')
    defect_dojo_key = os.getenv('DEFECT_DOJO_KEY')
    zap_topic = os.getenv('ZAP_TOPIC_NAME')
    gcp_project = os.getenv('GCP_PROJECT_ID')

    parser = argparse.ArgumentParser(description='Get scan types to run')
    parser.add_argument('-s', '--scans', nargs='+', default=[])

    args = parser.parse_args()

    endpoints = get_defect_dojo_endpoints(defect_dojo_url, defect_dojo_key)
    scan_endpoints(endpoints, gcp_project, zap_topic, args.scans)


if __name__ == '__main__':
    main()
