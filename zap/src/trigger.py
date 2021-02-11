#!/usr/bin/env python3
"""
Triggers ZAP scans for endpoints from DefectDojo.
"""

import argparse
from os import getenv
import re
from asyncio import Future
from typing import List, Literal, Optional, Set, TypedDict

import requests
from google.cloud.pubsub_v1 import PublisherClient

from zap import ScanType


class Endpoint(TypedDict):  # pylint: disable=inherit-non-class,too-few-public-methods
    """
    Defines she shape of an Endpoint object returned from DefectDojo.
    """

    protocol: Literal["http", "https"]
    host: str
    port: Optional[int]
    path: Optional[str]
    tags: List[str]


def get_defect_dojo_endpoints(base_url: str, api_key: str) -> List[Endpoint]:
    """
    Fetch endpoints from DefectDojo.
    """
    endpoint = base_url + "/api/v2/endpoints/"
    headers = {
        "content-type": "application/json",
        "Authorization": f"Token {api_key}",
    }
    res = requests.get(endpoint, headers=headers, timeout=30)
    res.raise_for_status()
    return res.json()["results"]


def pubsub_callback(endpoint: Endpoint):
    """
    Handle publish failures.
    """

    def callback(future: Future):
        try:
            print(future.result())
        except ConnectionRefusedError as err:
            print(f"Please handle {err} for {endpoint}.")

    return callback


def trigger_scan(  # pylint: disable=too-many-arguments
    publisher: PublisherClient,
    endpoint: Endpoint,
    topic: str,
    codedx_project: str,
    scan_type: ScanType,
    slack_channel: str,
):
    """
    Trigger scan for a given endpoint via a Pub/Sub message.
    """
    port = f":{endpoint['port']}" if endpoint["port"] else ""
    url = f"{endpoint['protocol']}://{endpoint['host']}{port}{endpoint['path'] or ''}"
    future = publisher.publish(
        topic=topic,
        data=b"",
        CODEDX_PROJECT=codedx_project,
        URL=url,
        SCAN_TYPE=scan_type.value,
        SLACK_CHANNEL=slack_channel,
    )
    future.add_done_callback(pubsub_callback(endpoint))


TAG_MATCHER = re.compile(r"^([^:]+):(.*)$")


def parse_tags(endpoint: Endpoint):
    """
    Parse tags for a given endpoint.
    """
    codedx_project = ""
    slack_channel = ""
    endpoint_scans: Set[ScanType] = set()
    for tag in endpoint["tags"]:
        tag_match = TAG_MATCHER.match(tag)
        if not tag_match:
            continue

        tag_key, tag_val = tag_match.group(1), tag_match.group(2)
        if tag_key == "codedx":
            codedx_project = tag_val
        if tag_key == "scan":
            endpoint_scans.add(ScanType(tag_val))
        if tag_key == "slack":
            slack_channel = tag_val
    return codedx_project, slack_channel, endpoint_scans


def trigger_scans(
    endpoints: List[Endpoint],
    gcp_project: str,
    topic_name: str,
    scan_types: List[ScanType],
):
    """
    Scan multiple endpoints by publishing multiple
    messages to a Pub/Sub topic with an error handler.
    """
    publisher = PublisherClient()
    topic = publisher.topic_path(gcp_project, topic_name)  # pylint: disable=no-member

    for endpoint in endpoints:
        codedx_project, slack_channel, endpoint_scans = parse_tags(endpoint)
        if not codedx_project:
            continue

        for scan_type in scan_types:
            if scan_type in endpoint_scans:
                trigger_scan(
                    publisher, endpoint, topic, codedx_project, scan_type, slack_channel
                )


def main():
    """
    - Fetch the list of endpoints from DefectDojo
    - Trigger the scans for all endpoints
    """
    defect_dojo_url = getenv("DEFECT_DOJO_URL")
    defect_dojo_key = getenv("DEFECT_DOJO_KEY")
    zap_topic = getenv("ZAP_TOPIC_NAME")
    gcp_project = getenv("GCP_PROJECT_ID")

    parser = argparse.ArgumentParser(description="Get scan types to run")
    parser.add_argument(
        "-s", "--scans", nargs="+", default=[], type=ScanType, choices=list(ScanType)
    )
    args = parser.parse_args()

    endpoints = get_defect_dojo_endpoints(defect_dojo_url, defect_dojo_key)
    trigger_scans(endpoints, gcp_project, zap_topic, args.scans)


if __name__ == "__main__":
    main()
