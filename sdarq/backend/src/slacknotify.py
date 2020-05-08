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
        attachments=[
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*New service engagement created* :books:"
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
                                "url": "{0}product/{1}" .format(dojo_host_url, str(product_id))
                            }
                        ]
                    }
                ],
                "color": "#0a88ab"
            }]
    )


def slacknotify_qa(slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url):
    """
    Sends slack notification where: 
        1. No Jira ticket is selected 
        2. QA person MUST be notified 

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
        attachments=[
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "@zbedo *New service engagement created* :books:"
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
                                "url": "{0}product/{1}" .format(dojo_host_url, str(product_id))
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
                      "text": "*New service engagement created* :books:"
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
                        "url": "{0}product/{1}" .format(dojo_host_url, str(product_id))
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


def slacknotify_jira_qa(slack_token, channel, dojo_name, security_champion, product_id, dojo_host_url, jira_instance, project_key_id, jira_ticket):
    """
    Sends slack notification where: 
        1. Jira ticket is selected 
        2. QA person MUST be notified 

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
                      "text": "@zbedo *New service engagement created* :books:"
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
                        "url": "{0}product/{1}" .format(dojo_host_url, str(product_id))
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
