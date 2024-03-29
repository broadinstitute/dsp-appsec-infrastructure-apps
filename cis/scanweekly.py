#!/usr/bin/env python3
"""
This module
- trigger PubSub to scan all projects in a list with prod projects
- finds all high vulnerabilities
- reports all high vulnerabilities to a Slack channel
"""
import concurrent
import os
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.publisher.futures import Future



def get_callback(data):
    """
    Handle publish failures
    """
    def callback(future: Future):
        try:
            print(future.result(), data)
        except:
            print(f"Please handle {future.exception()} for {data}.")

    return callback


def scan_projects(
    dataset_project_id: str,
    topic_name: str,
    slack_channel_weekly_report: str,
    sdarq_host: str,
    cis_prod_projects_list_final_list
):
    """
    Scan multiply projects by publishing multiple
    messages to a Pub/Sub topic with an error handler.

    Args:
       List of projects to be scanned
    Returns:
        Query results with all table names
    """
    message = "".encode("utf-8")

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(dataset_project_id, topic_name)

    formatted_slack_channel = f"#{slack_channel_weekly_report}"

    futures = []
    for prod_project in cis_prod_projects_list_final_list:
        results_url = f"{sdarq_host}/gcp-project-security-posture/results?project_id={prod_project}"
        future = publisher.publish(
            topic_path,
            data=message,
            GCP_PROJECT_ID=prod_project,
            SLACK_RESULTS_URL=results_url,
            SLACK_CHANNEL=formatted_slack_channel,
        )
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(prod_project))
        futures.append(future)
    concurrent.futures.wait(futures)


def main():
    """
    Implements the scanweekly.py
    """

    slack_channel_weekly_report = os.environ["SLACK_CHANNEL_WEEKLY_REPORT"]
    dataset_project_id = os.environ["DATASET_PROJECT_ID"]
    topic_name = os.environ["JOB_TOPIC"]
    sdarq_host = os.environ["SDARQ_HOST"]
    cis_prod_projects_list = os.getenv('CIS_PROD_PROJECTS', '')
    cis_prod_projects_list_final_list = cis_prod_projects_list.split(",")


    scan_projects(dataset_project_id, topic_name, slack_channel_weekly_report, sdarq_host, cis_prod_projects_list_final_list)


if __name__ == "__main__":
    main()
