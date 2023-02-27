#!/usr/bin/env python3
"""
This module
- will notify AppSec team in Slack for all security controls,
  that are not implemented for all services
"""

import os

from google.cloud import firestore
from slack_sdk import WebClient


def notify_appsec(security_controls_firestore_collection, slack_token, slack_channel, security_controls_ignore_final_list):
    """
    Get all security controls
    Check security controls that are set to false and not part of a FP list
    Report to a Slack channel
    """

    firestore_docs = firestore.Client()
    docs = firestore_docs.collection(security_controls_firestore_collection).stream()
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
        #Each doc represents a service and the list of security controls.
        #Each control is set to true or false.
        #This loops through every key in the dict to see if any are false.
        #This includes the 'service' key, and any other non-boolean key/value pairs.
        # for key in doc.to_dict():

        #     if doc.to_dict()[key] is False:
        #         service_name = doc.to_dict()['service'].strip(' ').replace(' ','_')
        #         service_seccon = f"{service_name}_{key}"
        #         if service_seccon in security_controls_ignore_final_list:
        #             continue

        #         client = WebClient(token=slack_token)
        #         client.chat_postMessage(
        #             channel=slack_channel,
        #             text="*AppSec Action Required*",
        #             attachments=[{"blocks": [
        #                 {
        #                     "type": "section",
        #                     "text": {
        #                         "type": "mrkdwn",
        #                         "text":
        #                             f"Security control `{keyword_maps[key]}` is not integrated/implemented for `{doc.to_dict()['service'].capitalize()}`.",
        #                     }
        #                 },
        #             ], "color": "#C31818"}]
        #         )
        doc_dict = doc.to_dict()
        service = doc_dict['service'].strip(' ').replace(' ','_')
        control_list = list()
        for key in keyword_maps:
            if doc_dict[key] is False and f"{service}_{key}" not in security_controls_ignore_final_list:
                control_list.append(f"`{key}`")
        
        #build string of missing controls
        control_string="\n".join(control_list)

        #build attachment. 
        attachment = dict()
        attachment['blocks'] = list()
        attachment['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text":
                        f"The following security controls are not integrated/implemented for `{service.capitalize()}`.\n\n{control_string}",
                    }
                })
        attachment['color'] = "#C31818"

        client = WebClient(token=slack_token)
        client.chat_postMessage(
            channel=slack_channel,
            text="*AppSec Action Required*",
            attachments=[attachment]
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

    notify_appsec(security_controls_firestore_collection, slack_token,
                  slack_channel, security_controls_ignore_final_list)


if __name__ == "__main__":
    main()
