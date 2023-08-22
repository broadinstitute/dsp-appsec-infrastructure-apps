#!/usr/bin/env python3

import ssl
import os
from slack_sdk import WebClient
from typing import Any, List, Set

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

slack_token = os.getenv('slack_token')

client = WebClient(token=slack_token,
                         ssl=ssl_context)

def slack_notify(target_project_id: str, slack_token: str, slack_channel: str, results_url: str):
    """
    Posts a notification about results to Slack.
    """
    client = WebClient(token=slack_token)
    client.chat_postMessage(
        channel=slack_channel,
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Check `{target_project_id}` CIS scan results :spiral_note_pad:",
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Get results"
                        },
                        "url": results_url,
                    }
                ]
            }], "color": "#0731b0"}]
    )


def find_highs(rows: List[Any], slack_channel: str, slack_token: str, target_project_id: str):
    """
    Find high vulnerabilities from GCP project scan.
    Args:
       List of project findings, slack channel, slack token
    Returns:
        None
    """
    records = []
    for row in rows:
        if row['failures'] and float(row['impact']) > 0.6:
            records.append({
                'impact': row['impact'],
                'title': row['title'],
                'description': row['description']
            })
    if records:
        slack_notify_high(records, slack_token,
                          slack_channel, target_project_id)


def slack_notify_high(records: List[Any], slack_token: str,
                      slack_channel: str, target_project_id: str):
    """
    Post notifications in Slack
    about high findings
    """
    client = WebClient(token=slack_token)
    for row in records:
        client.chat_postMessage(
            channel=slack_channel,
            attachments=[{"blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":
                            f"* | High finding in `{target_project_id}` GCP project* :gcpcloud: :",
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Impact*: `{float(row['impact'])*10}`",

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Title*: `{row['title']}`",

                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description* `{row['description']}`",

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
                            "image_url":
                            "https://platform.slack-edge.com/img/default_application_icon.png",
                            "alt_text": "slack"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*GCP* Project Weekly Scan"
                        }
                    ]
                }
            ], "color": "#C31818"}]
        )

def slack_error(slack_token ,slack_channel, error, target_project_id):
    """
    This functions sends an alert if there is scanning error
    """
    client = WebClient(token=slack_token)
    client.chat_postMessage(
            channel=slack_channel,
            attachments=[{"blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text":
                            f"* Error raised while running `{target_project_id}` GCP project* :gcpcloud: :",
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Error: {error}"

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
                            "image_url":
                            "https://platform.slack-edge.com/img/default_application_icon.png",
                            "alt_text": "slack"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*GCP* Project Weekly Scan"
                        }
                    ]
                }
            ], "color": "#CD0000"}]
        )