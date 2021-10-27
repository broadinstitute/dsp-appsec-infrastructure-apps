#!/usr/bin/env python3
"""
This module
- get all security controls for each service
- send notifications/reminder to Appsec team for missing security controls
"""

import os

from google.cloud import firestore

import slacknotify


def get_sec_controls(security_controls_firestore_collection, slack_channel):
    """
    Get all data from Firestore
    Args: None
    Returns: Json data
    """
    
    db = firestore.Client()
    docs = db.collection(security_controls_firestore_collection).stream()
    for doc in docs:
        service = doc.to_dict()
        if service.get('sourceclear') is None or service['sourceclear'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'Sourceclear')
        if service.get('docker_scan') is None or service['docker_scan'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'Docker scan')
        if service.get('burp') is None or service['burp'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'Security manual pentest')
        if service.get('zap') is None or service['zap'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'DAST')
        if service.get('cis_scanner') is None or service['cis_scanner'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'CIS scanner')
        if service.get('threat_model') is None or service['threat_model'] is False:
            slacknotify.slacknotify_security_controls(slack_channel, service['service'], 'Threat Model')

def main():
    """
    Implements the security-controls-reminder.py
    """

security_controls_firestore_collection = os.environ['SC_FIRESTORE_COLLECTION']
slack_channel = os.getenv('appsec_slack_channel')

get_sec_controls(security_controls_firestore_collection, slack_channel)

if __name__ == "__main__":
    main()
