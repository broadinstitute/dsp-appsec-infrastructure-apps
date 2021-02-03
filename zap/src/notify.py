import os
from slack_sdk.web import WebClient

def slack_message(channel, msg):
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    response = client.chat_postMessage(
        channel=channel,
        text=msg)
    if response.status_code != 200:
        print(f'Response from slack returned an error: {response.body}')
