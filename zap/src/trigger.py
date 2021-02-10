#!/usr/bin/env python3

import argparse
import os
import re
from asyncio import Future
from typing import List, Set

import requests
from google.cloud import pubsub_v1

from scan import SEVERITY_DELIM
from zap import ScanType


def get_defect_dojo_endpoints(base_url: str, api_key: str):
    endpoint = base_url + "/api/v2/endpoints/"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {api_key}",
    }
    r = requests.get(endpoint, headers=headers, timeout=30)
    r.raise_for_status()
    endpoints = r.json()["results"]
    return endpoints


def pubsub_callback(endpoint: str):
    """Handle publish failures."""

    def callback(future: Future):
        try:
            print(future.result())
        except Exception as err:
            print("Please handle {} for {}.".format(err, endpoint))

    return callback


def scan_endpoints(
    endpoints, gcp_project: str, topic_name: str, scan_types: List[ScanType]
):
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
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(gcp_project, topic_name)

    tag_matcher = re.compile(r"^([^:]+):(.*)$")

    for endpoint in endpoints:
        codedx_project = ""
        slack_channel = ""
        severities: Set[str] = set()
        endpoint_scans: Set[ScanType] = set()
        for tag in endpoint["tags"]:
            tag_match = tag_matcher.match(tag)
            if not tag_match:
                continue

            tag_key, tag_val = tag_match.group(1), tag_match.group(2)
            if tag_key == "codedx":
                codedx_project = tag_val
            if tag_key == "scan":
                endpoint_scans.add(ScanType(tag_val))
            if tag_key == "severity":
                severities.add(tag_val)
            if tag_key == "slack":
                slack_channel = tag_val

        if not codedx_project:
            continue

        for scan_type in scan_types:
            if scan_type not in endpoint_scans:
                continue

            port = endpoint["port"] or ""
            url = f"{endpoint['protocol']}://{endpoint['host']}{port}{endpoint['path']}"
            future = publisher.publish(
                topic_path,
                data=b"",
                CODEDX_PROJECT=codedx_project,
                URL=url,
                SCAN_TYPE=scan_type.value,
                SLACK_CHANNEL=slack_channel,
                SEVERITIES=SEVERITY_DELIM.join(severities),
            )
            future.add_done_callback(pubsub_callback(endpoint))


def main():
    defect_dojo_url = os.getenv("DEFECT_DOJO_URL")
    defect_dojo_key = os.getenv("DEFECT_DOJO_KEY")
    zap_topic = os.getenv("ZAP_TOPIC_NAME")
    gcp_project = os.getenv("GCP_PROJECT_ID")

    parser = argparse.ArgumentParser(description="Get scan types to run")
    parser.add_argument(
        "-s", "--scans", nargs="+", default=[], type=ScanType, choices=list(ScanType)
    )
    args = parser.parse_args()

    endpoints = get_defect_dojo_endpoints(defect_dojo_url, defect_dojo_key)
    scan_endpoints(endpoints, gcp_project, zap_topic, args.scans)


if __name__ == "__main__":
    main()
