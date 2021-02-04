import os
from slack_sdk.web import WebClient

def slack_message(channel, msg):
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    response = client.chat_postMessage(
        channel=channel,
        text=msg)
    if response.status_code != 200:
        print(f'Response from slack returned an error: {response.body}')

def slack_attach(channel, filename):
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    response = client.chat_postMessage(
        channel=channel,
        text="Please see attached report."
    )

    if response.status_code != 200:
        print(f'Response from slack returned an error: {response.body}')
    
    file_path = filename

    with open(file_path , "rb"):
        response = client.files_upload(
            channels=channel,
            file=file_path,
            title=filename,
            filetype='pdf'
        )

    if response.status_code != 200:
        print(f'Response from slack file upload returned an error: {response.body}')