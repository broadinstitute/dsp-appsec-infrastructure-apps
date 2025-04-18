#!/usr/bin/env python3
"""
Triggers ZAP scans for endpoints from DefectDojo.
"""

import argparse
import concurrent
import logging
import google.cloud.logging
import re
import traceback
from asyncio import Future
from os import getenv
from typing import List, Literal, Optional, Set, TypedDict

import requests
from google.cloud.pubsub_v1 import PublisherClient
from zap_scan_type import ScanType


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
    # Fetch endpoints that have been tagged with scan:*
    # It is unlikely that there are more than 1000 of them
    endpoint = base_url + "/api/v2/endpoints?limit=1000&tag=scan"
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
            logging.info(f"PSC {future.result()}")
        except ConnectionRefusedError as err:
            logging.error(f"Please handle {err} for {endpoint}.")

    return callback


def trigger_scan(  # pylint: disable=too-many-arguments
    publisher: PublisherClient,
    endpoint: Endpoint,
    topic: str,
    codedx_project: str,
    scan_type: ScanType,
    slack_channel: str,
    product_id: str,
):
    """
    Trigger scan for a given endpoint via a Pub/Sub message.
    """
    port = f":{endpoint['port']}" if endpoint["port"] else ""
    url = f"{endpoint['protocol']}://{endpoint['host']}{port}/{endpoint['path'] or ''}"
    future = publisher.publish(
        topic=topic,
        data=b"",
        CODEDX_PROJECT=codedx_project,
        URL=url,
        SCAN_TYPE=scan_type.name,
        SLACK_CHANNEL=slack_channel,
        PRODUCT_ID=product_id,
    )
    future.add_done_callback(pubsub_callback(endpoint))
    return future


TAG_MATCHER = re.compile(r"^([^:]+):(.*)$")


def parse_tags(endpoint: Endpoint):
    """
    Parse tags for a given endpoint.
    """
    codedx_project = ""
    slack_channel = ""
    scan_type: Optional[ScanType] = None
    product_id = ""
    for tag in endpoint["tags"]:
        tag_match = TAG_MATCHER.match(tag)
        if not tag_match:
            continue

        tag_key, tag_val = tag_match.group(1), tag_match.group(2)
        if tag_key == "codedx":
            codedx_project = tag_val
        if tag_key == "scan":
            try:
                scan_type = ScanType[tag_val.upper()]
            except Exception:
                scan_type = ""
        if tag_key == "slack":
            slack_channel = tag_val
        if tag_key == "product_id":
            product_id = tag_val
    return codedx_project, slack_channel, scan_type, product_id


def trigger_scans(
    endpoints: List[Endpoint],
    gcp_project: str,
    topic_name: str,
    scan_types: Set[ScanType],
):
    """
    Scan multiple endpoints by publishing multiple
    messages to a Pub/Sub topic with an error handler.
    """
    publisher = PublisherClient()
    topic = publisher.topic_path(gcp_project, topic_name)  # pylint: disable=no-member

    futures = []
    for endpoint in endpoints:
        slack_channel = None
        try:
            codedx_project, slack_channel, scan_type, product_id = parse_tags(endpoint)
            if scan_type in scan_types:
                future = trigger_scan(
                    publisher, endpoint, topic, codedx_project, scan_type, slack_channel, product_id
                )
                futures.append(future)
        except BaseException as base_error: # pylint: disable=bare-except
            logging.error(f"Error triggering scan for: { endpoint }\n{ traceback.print_exc() }")
            raise base_error

    concurrent.futures.wait(futures)


def main():
    """
    - Fetch the list of endpoints from DefectDojo
    - Trigger the scans for all endpoints
    """
    client = google.cloud.logging.Client()
    client.setup_logging()
    defectdojo_url = getenv("DEFECT_DOJO_URL")
    defect_dojo_key = getenv("DEFECT_DOJO_KEY")
    zap_topic = getenv("ZAP_TOPIC_NAME")
    gcp_project = getenv("GCP_PROJECT_ID")
    logging.info(f"Cron job running. Dojo {defectdojo_url} Topic {zap_topic} Project {gcp_project}")
    parser = argparse.ArgumentParser(description="Get scan types to run")
    parser.add_argument(
        "-s",
        "--scans",
        nargs="+",
        default=[],
        type=str,
        choices=[s.name.lower() for s in list(ScanType)],
    )

    args = parser.parse_args()
    scan_types = set(ScanType[s.upper()] for s in args.scans)
    logging.info(f"Scan types: { args.scans }")


    endpoints = get_defect_dojo_endpoints(defectdojo_url, defect_dojo_key)
    logging.info(f"Defect Dojo {len(endpoints) if endpoints else 'no'} endpoints fetched.")

    trigger_scans(endpoints, gcp_project, zap_topic, scan_types)


if __name__ == "__main__":
    main()
