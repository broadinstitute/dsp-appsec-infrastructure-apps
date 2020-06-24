#!/usr/bin/env python3
"""
This module
- lists all projects from BigQuery
- trigger PubSub to scan all projects listed from BigQuery
- finds all high vulnerabilities
- reports all high vulnerabilities to a Slack channel
"""
import os
from typing import List, Any
import slack
from google.cloud import bigquery, pubsub_v1

futures = dict()


def list_projects(project_id: str, bq_dataset: str):
    """
    Fetch all tables in BigQuery
    Args:
       None
    Returns:
        List of table names in BigQuery
    """
    client = bigquery.Client()

    dataset_id = u"{0}.{1}".format(project_id, bq_dataset)

    tables = list(client.list_tables(dataset_id))

    return tables


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


def scan_projects(tables: List[Any], project_id: str, topic_name: str, slack_channel: str):
    """
    Scan multiply projects by publishing multiple
    messages to a Pub/Sub topic with an error handler.

    Args:
       List of projects to be scanned
    Returns:
        Query results with all table names
    """
    message = ""
    message = message.encode("utf-8")

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)

    for table in tables:
        data = u"{}".format(table.table_id)
        gcp_project_id = str(table.table_id).replace('_', '-')
        # When a message is published, the client returns a future.
        future = publisher.publish(
            topic_path,
            data=message,
            GCP_PROJECT_ID=gcp_project_id,
            SLACK_CHANNEL=slack_channel
        )
        futures[data] = future
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(future, data))


def main():
    """
    Implements the scanweekly.py
    """

    bq_dataset = os.environ['BQ_DATASET']
    slack_channel = os.environ['SLACK_CHANNEL']
    project_id = os.environ['PROJECT_ID']
    topic_name = os.environ['JOB_TOPIC']

    tables = list_projects(project_id, bq_dataset)

    scan_projects(tables, project_id, topic_name, slack_channel)


if __name__ == '__main__':
    main()
