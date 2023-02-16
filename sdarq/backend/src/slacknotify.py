#!/usr/bin/env python3

import ssl
import os
from slack_sdk import WebClient

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

slack_token = os.getenv('slack_token')

client = WebClient(token=slack_token,
                         ssl=ssl_context)


def slacknotify_app_jira(appsec_slack_channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket):
    """
    Sends slack notification when there is:
        1. New app 
        2. Jira ticket is selected 

    Args:
        appsec_slack_channel: Slack channel name
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
    client.chat_postMessage(
        channel=appsec_slack_channel,
        text="New APP created",
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*App name:* {0} " .format(str(dojo_name))
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
        ], "color": "#0731b0"}]
    )

def slacknotify_jira(appsec_slack_channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket):
    """
    Sends slack notification when there is: 
        1. New service
        2. Jira ticket is selected 

    Args:
        appsec_slack_channel: Slack channel name
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
    client.chat_postMessage(
        channel=appsec_slack_channel,
        text="New service created",
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Service name:* {0} " .format(str(dojo_name))
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
        ], "color": "#0731b0"}]
    )

def slacknotify_threat_model(appsec_slack_channel, user_email, request_type, project_name,  jira_instance, jira_ticket_appsec, appsec_jira_board):
    """
    Sends slack notification when there is a request for threat model

    Args:
        appsec_slack_channel: Slack channel name
        security_champion: Security champion name
        request_type: Create or update threat model
        project_name: Project name
        jira_instance:  Jira Cloud instance
        jira_ticket: Jira ticket path 
        appsec_jira_board: Jira appsec project key id 

    Returns:
        Sends slack notification
    """
    client.chat_postMessage(
        channel=appsec_slack_channel,
        text="There is a request for a threat model",
        attachments=[{"blocks":[
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
                    "text": "*Security champion:* {0} " .format(parse_user_email(user_email))
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
        ], "color": "#0731b0"}]
    )

def slacknotify_security_pentest(appsec_slack_channel, user_email, project_name, jira_instance, jira_ticket_appsec, appsec_jira_board):
    """
    Sends slack notification when there is a request for a security request

    Args:
        appsec_slack_channel: Slack channel name
        security_champion: Security champion name
        project_name: Project name
        jira_instance:  Jira Cloud instance
        jira_ticket: Jira ticket path 
        appsec_jira_board: Jira appsec project key id 

    Returns:
        Sends slack notification
    """
    client.chat_postMessage(
        channel=appsec_slack_channel,
        text="There is a security pentest request",
        attachments=[{"blocks":[
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
                    "text": "*Security champion:* {0} " .format(parse_user_email(user_email))
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
        ], "color": "#0731b0"}]
    )

def slacknotify_jira_ticket_risk_assessment(jtra_slack_channel, ticket_context, user_email, user_data, due_date):
    """
    Sends Slack notifications to AppSec when there is high risk Jira ticket

    Args:
        jtra_slack_channel: Jira Ticket Risk Assessment Slack channel 
        jira_ticket_link: Jira ticket link
        user_email: Dev email that filled the form
        user_data: All data submitted by users

    Returns:
        Sends slack notification
    """
    client.chat_postMessage(
        channel=jtra_slack_channel,
        text="HIGH Risk Jira Ticket",
        attachments=[{"blocks":[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Ticket link/context:* `{0}` " .format(str(ticket_context))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Dev:* `{0}` " .format(parse_user_email(user_email))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*AppSec Due Date:* `{0}` " .format(str(due_date))
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*All user's data:* `{0}` " .format(str(user_data))
                }
            }
        ], "color": "#bd3022"}]
    )

def slacknotify_jira_ticket_risk_assessment_error(jtra_slack_channel, user_email, user_data):
    """
    Sends Slack notifications to AppSec when there is an error happening in the server

    Args:
        jtra_slack_channel: Jira Ticket Risk Assessment Slack channel 
        user_email: Dev email that filled the form
        user_data: All data submitted by users

    Returns:
        Sends slack notification
    """
    client.chat_postMessage(
        channel=jtra_slack_channel,
        text="An error happened to Jira Ticket Risk Assessment questionnaire",
        attachments=[{"blocks":[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Dev:* `{0}` " .format(parse_user_email(user_email))
                }
            },
                        {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*All user's data:* `{0}` " .format(str(user_data))
                }
            }
        ], "color": "#bd3022"}]
    )

