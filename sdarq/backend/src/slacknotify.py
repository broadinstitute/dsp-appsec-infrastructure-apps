#!/usr/bin/env python3

import slack


def slacknotify(slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url):
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
    client = slack.WebClient(slack_token)
    response = client.chat_postMessage(
        channel=channel,
        attachments=[{"blocks": [
            {
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*New service engagement created*"
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
        ],
            "color": "#0a88ab"
        }]
    )


def slacknotify_jira(slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket):
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
    client = slack.WebClient(slack_token)
    response = client.chat_postMessage(
        channel=channel,
        attachments=[{"blocks": [
            {
                "type": "section",
                "text": {
                      "type": "mrkdwn",
                      "text": "*New service engagement created*"
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
        ],
            "color": "#0a88ab"
        }]
    )


def slacknotify_threat_model(slack_token, channel, security_champion, request_type, project_name,  jira_instance, jira_ticket_appsec, appsec_jira_board):
    """
    Sends slack notification there is a request for threat model

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
    client = slack.WebClient(slack_token)
    response = client.chat_postMessage(
        channel=channel,
        attachments=[{"blocks": [
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
        ],
            "color": "#0a88ab"
        }]
    )
