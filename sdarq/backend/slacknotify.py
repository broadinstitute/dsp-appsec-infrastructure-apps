import slack

def slacknotify(slack_token, channel, appName, securityChamp, product_id, dojo_host):
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
                                "text": "*Product name:* {0} " .format(str(appName))
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Security champion:* {0} " .format(str(securityChamp))
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
                                    "url": "{0}product/{1}" .format(dojo_host, str(product_id))
                                }
                            ]
                        }
                    ],
                  "color": "#0a88ab"
                } ]
            )

def slacknotifyQAperson(slack_token, channel, appName, securityChamp, product_id, dojo_host):
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
                                "text": "@gary_dlugy *New service engagement created* :books:"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Product name:* {0} " .format(str(appName))
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Security champion:* {0} " .format(str(securityChamp))
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
                                    "url": "{0}product/{1}" .format(dojo_host, str(product_id))
                                }
                            ]
                        }
                    ],
                  "color": "#0a88ab"
                } ]
            )

def slacknotifyjira(slack_token, channel, appName, securityChamp, product_id, dojo_host, jira_instance, project_key_id, jira_ticket):
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
                                "text": "*Product name:* {0} " .format(str(appName))
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Security champion:* {0} " .format(str(securityChamp))
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
                                    "url": "{0}product/{1}" .format(dojo_host, str(product_id))
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
                } ]
            )

def slacknotifyjiraQAperson(slack_token, channel, appName, securityChamp, product_id, dojo_host, jira_instance, project_key_id, jira_ticket):
              client = slack.WebClient(slack_token)
              response = client.chat_postMessage(
              channel=channel,
              attachments=[{"blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "@gary_dlugy *New service engagement created* :books:"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Product name:* {0} " .format(str(appName))
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Security champion:* {0} " .format(str(securityChamp))
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
                                    "url": "{0}product/{1}" .format(dojo_host, str(product_id))
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
                } ]
            )
