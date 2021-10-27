#!/usr/bin/env python3

import ssl
import os
from slack_sdk import WebClient

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

slack_token = os.getenv('slack_token')

client = WebClient(token=slack_token,
                         ssl=ssl_context)


def slacknotify(channel, dojo_name, security_champion, product_id, dojo_host_url):
    """
    Sends slack notification where: 
        1. No Jira ticket is selected 
        2. No QA person must be notified 

    Args:
        slack_token: Slack token 
        channel: Slack channel name
        dojo_name: Engagement name in defect dojo
        security_champion: Security champion name
        product_id: Product in defectdojo
        dojo_host: DefectDojo host

    Returns:
        Sends slack notification
    """
    response = client.chat_postMessage(
        channel=channel,
        text="New service created",
        blocks=[
            {
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*New service created*"
                        }
            },
            {
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Product name:* {0} " .format(str(dojo_name))
                        }
            },
            {
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Security champion:* {0} " .format(str(security_champion))
                        }
            },
            {
                "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Defect Dojo"
                                },
                                "url": "{0}/product/{1}" .format(dojo_host_url, str(product_id))
                            }
                        ]
            }
        ]
    )


def slacknotify_jira(channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket):
    """
    Sends slack notification where: 
        1. Jira ticket is selected 
        2. QA person will not be notified 

    Args:
        slack_token: Slack token 
        channel: Slack channel name
        dojo_name: Engagement name in defect dojo
        security_champion: Security champion name
        product_id: Product in defectdojo
        dojo_host: DefectDojo host
        jira_instance:  Jira Cloud instance
        project_key_id: Jira project id
        jira_ticket: Jira ticket path 

    Returns:
        Sends slack notification
    """
    response = client.chat_postMessage(
        channel=channel,
        text="New service created",
        blocks=[
            {
                "type": "section",
                "text": {
                      "type": "mrkdwn",
                      "text": "*New service created*"
                      }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Product name:* {0} " .format(str(dojo_name))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Security champion:* {0} " .format(str(security_champion))
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Defect Dojo"
                        },
                        "url": "{0}/product/{1}" .format(dojo_host_url, str(product_id))
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Jira Ticket"
                        },
                        "url": "{0}/projects/{1}/issues/{2}" .format(jira_instance, str(project_key_id), str(jira_ticket))
                    }
                ]
            }
        ]
    )


def slacknotify_threat_model(channel, security_champion, request_type, project_name,  jira_instance, jira_ticket_appsec, appsec_jira_board):
    """
    Sends slack notification when there is a request for threat model

    Args:
        slack_token: Slack token 
        channel: Slack channel name
        security_champion: Security champion name
        request_type: Create or update threat model
        project_name: Project name
        jira_instance:  Jira Cloud instance
        jira_ticket: Jira ticket path 
        appsec_jira_board: Jira appsec project key id 

    Returns:
        Sends slack notification
    """
    response = client.chat_postMessage(
        channel=channel,
        text="There is a request for a threat model",
        blocks=[
            {
                "type": "section",
                "text": {
                      "type": "mrkdwn",
                      "text": "*{0}*" .format(str(request_type))
                      }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Project:* {0} " .format(str(project_name))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Security champion:* {0} " .format(str(security_champion))
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Jira Ticket"
                        },
                        "url": "{0}/projects/{1}/issues/{2}" .format(jira_instance, str(appsec_jira_board), str(jira_ticket_appsec))
                    }
                ]
            }
        ]
    )

def slacknotify_security_pentest(channel, security_champion, project_name, jira_instance, jira_ticket_appsec, appsec_jira_board):
    """
    Sends slack notification when there is a request for a security request

    Args:
        slack_token: Slack token 
        channel: Slack channel name
        security_champion: Security champion name
        project_name: Project name
        jira_instance:  Jira Cloud instance
        jira_ticket: Jira ticket path 
        appsec_jira_board: Jira appsec project key id 

    Returns:
        Sends slack notification
    """
    response = client.chat_postMessage(
        channel=channel,
        text="There is a request for security pentest",
        blocks=[
            {
                "type": "section",
                "text": {
                      "type": "mrkdwn",
                      "text": "*There is a security pentest request*"
                      }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Project:* {0} " .format(str(project_name))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Security champion:* {0} " .format(str(security_champion))
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Jira Ticket"
                        },
                        "url": "{0}/projects/{1}/issues/{2}" .format(jira_instance, str(appsec_jira_board), str(jira_ticket_appsec))
                    }
                ]
            }
        ]
    )

def slacknotify_security_controls(channel, service, missing_control):
    response = client.chat_postMessage(
    channel=channel,
    text="There is a request for security pentest",
    blocks=[
        {
            "type": "section",
            "text": {
                    "type": "mrkdwn",
                    "text": "*Security Control Not Implemented*"
                    }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Service:* {0} " .format(str(service))
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Missing security control:* {0} " .format(str(missing_control))
            }
        }
    ]
)

