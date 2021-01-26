#!/usr/bin/env python3
"""
This module
- fetches a list of endpoint object from defect dojo
- formats the endpoint object as a pubsub message
"""
import os
from google.cloud import pubsub_v1
import requests

futures = dict()

def get_defect_dojo_endpoints(url, key):
    endpoint = 'https://{}/api/v2/endpoints/'.format(url)
    token = 'Token {}'.format(key)

    headers = {'content-type': 'application/json',
            'Authorization': token}
    r = requests.get(endpoint, headers=headers, verify=True) # set verify to False if ssl cert is self-signed

    endpoints = r
    if r.status_code != 200:
        print(r.text)

    endpoints = r.json()["results"]

    return endpoints

def get_callback(future, data):
    """
    Handle publish failures
    """
    def callback(future):
        try:
            print(future.result())
            futures.pop(data)
        except:
            print("Please handle {} for {}.".format(future.exception(), data))

    return callback


def scan_endpoints(endpoints, gcp_project, topic_name):
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
        codedx_project = None
        for tag in endpoint["tags"]:
            # endpoints to scan will include tag codedx:CODEDX_PROJECT to identify project on codedx
            if "codedx" in tag:
                codedx_project = "".join(tag.split(":")[1:])
        if codedx_project is not None:   
            for scan_type in endpoint["tags"]:
                if scan_type in ["baseline-scan", "api-scan", "auth-scan", "ui-scan"]:
                    url = f"{endpoint['protocol']}://{endpoint['host']}"

                    # When a message is published, the client returns a future.
                    future = publisher.publish(
                        topic_path,
                        data=message,
                        CODEX_PROJECT=codedx_project,
                        URL=url,
                        SCAN_TYPE=scan_type
                    )
                    futures[data] = future
                    # Publish failures shall be handled in the callback function.
                    future.add_done_callback(get_callback(future, data))

def main():
    defect_dojo_url = os.getenv('DEFECT_DOJO_URL')
    defect_dojo_key = os.getenv('DEFECT_DOJO_KEY')
    zap_topic = os.getenv('ZAP_TOPIC_NAME')
    gcp_project = os.getenv('GCP_PROJECT_ID')

    endpoints = get_defect_dojo_endpoints(defect_dojo_url, defect_dojo_key)
    scan_endpoints(endpoints, gcp_project, zap_topic)

if __name__ == '__main__':
    main()
