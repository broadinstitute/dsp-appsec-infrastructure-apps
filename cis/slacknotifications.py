#!/usr/bin/env python3
"""
This module
- send slack notifications about results, high findings of level 1 and errors raised.
"""

import ssl
from typing import Any, List
from slack_sdk import WebClient


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED


def slack_notify(target_project_id: str, slack_token: str, slack_channel: str, results_url: str):
    """
    Posts a notification about results to Slack.
    """
    client = WebClient(token=slack_token, ssl=ssl_context)
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


def slack_notify_high(records: List[Any], slack_token: str,
                      slack_channel: str, target_project_id: str):
    """
    Post notifications in Slack about high findings
    """
    client = WebClient(token=slack_token, ssl=ssl_context)
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
    client = WebClient(token=slack_token, ssl=ssl_context)
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
