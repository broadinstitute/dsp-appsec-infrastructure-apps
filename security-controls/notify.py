#!/usr/bin/env python3
"""
This module
- will notify AppSec team in slack for all security controls that are not implemented for specific services
"""

import os, logging
import requests
from google.cloud import firestore
from slack_sdk import WebClient


def notify_appsec(security_controls_firestore_collection, slack_token, slack_channel, security_controls_ignore_final_list):
    db = firestore.Client()
    data = []

    docs = db.collection(security_controls_firestore_collection).stream()
    for doc in docs:
        for key in doc.to_dict():
            if doc.to_dict()[key] == False:
                service_seccon =  f"{doc.to_dict()['service']}_{key}"
                if service_seccon in security_controls_ignore_list:
                    continue
                else
                    client = WebClient(token=slack_token)
                    client.chat_postMessage(
                        channel=slack_channel,
                        attachments=[{"blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text":
                                        f"Security control {key} is not integrated for this service/app {doc.to_dict()['service']}!",
                                }
                            },
                            {
                                "type": "divider"
                            },
                        ], "color": "#C31818"}]
                    )



def main():
    """
    Implements the entrypoint.
    """
    security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']
    slack_token = os.getenv('SLACK_TOKEN')
    slack_channel = os.getenv('SLACK_CHANNEL')
    security_controls_ignore_list = os.getenv('SECURITY_CONTROLS_IGNORE', '')
    security_controls_ignore_final_list = security_controls_ignore_list.split(",")

    notify_appsec(security_controls_firestore_collection, slack_token, slack_channel, security_controls_ignore_final_list)

if __name__ == "__main__":
    main()
