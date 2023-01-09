#!/usr/bin/env python3
"""
This module
- will notify AppSec team in slack for all security controls that are not implemented for specific services
"""

import os
from google.cloud import firestore
from slack_sdk import WebClient


def notify_appsec(security_controls_firestore_collection, slack_token, slack_channel, security_controls_ignore_final_list):
    db = firestore.Client()
    docs = db.collection(security_controls_firestore_collection).stream()

    keyword_maps = {
        "burp": "security manual pentest",
        "zap": "DAST",
        "cis_scanner": "CIS scanner",
        "sourceclear": "3rd party dependencies scan",
        "docker_scan": "container image scan",
        "threat_model": "threat model",
        "sast": "SAST"
    }

    for doc in docs:
        for key in doc.to_dict():
            if doc.to_dict()[key] is False:
                service_seccon =  f"{doc.to_dict()['service']}_{key}"
                if service_seccon in security_controls_ignore_final_list:
                    continue
                
                client = WebClient(token=slack_token)
                client.chat_postMessage(
                    channel=slack_channel,
                    text="AppSec reminder",
                    attachments=[{"blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text":
                                    f"Security control `{keyword_maps[key]}` is not integrated for {doc.to_dict()['service']}!",
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