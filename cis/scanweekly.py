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

slack_token = os.environ['SLACK_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL']
project_id = os.getenv('PROJECT_ID')
bq_dataset = os.getenv('BQ_DATASET')
topic_name = os.getenv('JOB_TOPIC')

client = bigquery.Client()

futures = dict()


def list_projects():
    """
    Fetch all tables in BigQuery
    Args:
       None
    Returns:
        List of table names in BigQuery
    """
    sql_tables = """
            SELECT table_name FROM `cis.INFORMATION_SCHEMA.TABLES`
            """
    query_job_table = client.query(sql_tables)
    results_table = query_job_table.result()

    return results_table


def get_callback(f, data):
    """
    Handle publish failures
    """
    def callback(f):
        try:
            print(f.result())
            futures.pop(data)
        except:
            print("Please handle {} for {}.".format(f.exception(), data))

    return callback


def scan_projects(projects: List[Any]):
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

    for row in projects:
        data = u"{}".format(row['table_name'])
        futures.update({data: None})
        gcp_project_id = row['table_name'].replace('_', '-')
        # When a message is published, the client returns a future.
        future = publisher.publish(
            topic_path,
            data=message,
            GCP_PROJECT_ID=gcp_project_id
        )
        futures[data] = future
        # Publish failures shall be handled in the callback function.
        future.add_done_callback(get_callback(future, data))


def find_highs(projects: List[Any]):
    """
    Find high vulnerabilities from GCP project scan.

    Args:
       List of projects to be scanned
    Returns:
        None
    """
    for row in projects:
        user_proj = row['table_name']
        print(user_proj)

        sql = "SELECT * FROM `{0}.{1}.{2}` WHERE impact>'0.6' ".format(
            str(project_id), str(bq_dataset), str(row['table_name']))
        query_job = client.query(sql)
        query_job.result()
        records = [dict(row) for row in query_job]
        slack_notify(records, slack_token, slack_channel, user_proj)


def slack_notify(records: str, slack_token: str, slack_channel: str, user_proj: str):
    """
    Post notifications in Slack
    about high findings
    """
    client = slack.WebClient(slack_token)
    for row in records:
        client.chat_postMessage(
            channel=slack_channel,
            attachments=[{"blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "* | High finding in  `{0}` GCP project* :gcpcloud: :" .format(user_proj.replace('_', '-'))
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Impact*: `{0}`" .format(str(float(row['impact'])*10))

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Title*: `{0}`" .format(row['title'])

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Description* `{0}`" .format(row['description'])

                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": "https://platform.slack-edge.com/img/default_application_icon.png",
                            "alt_text": "slack"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*GCP* Project Weekly Scan"
                        }
                    ]
                }
            ],
                          "color": "#C31818"}]
        )


def main():
    """
    Implements the scanweekly.py
    """

    # scan_projects(list_projects())
    find_highs(list_projects())


if __name__ == '__main__':
    main()
