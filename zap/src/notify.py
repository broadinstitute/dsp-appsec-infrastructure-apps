import os

from slack_sdk import WebhookClient


def slack_message(msg):
    slack_url = os.getenv('SLACK_WEBHOOK')
    webhook = WebhookClient(slack_url)
    response = webhook.send(text=msg)
    if response.status_code != 200:
        print(f'Response from slack returned an error: {response.body}')
