#!/usr/bin/env python3
# Pull subscriber

import json
import os
from codedx_api import CodeDxAPI
from google.cloud import pubsub_v1, storage
from slack import WebhookClient
from dateutil import tz, parser
from datetime import datetime
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=3600)

codedx_api_key = os.environ['codedx_api_key']
project_id = os.environ['PROJECT_ID']
subscription_name = os.environ['SUBSCRIPTION']
base_url = os.environ['CODEDX_URL']
slack_url = os.environ['slack_webhook']
webhook = WebhookClient(slack_url)

def callback(message):
    try:
        data = message.data.decode('utf-8')
        attributes = message.attributes
        message_id = attributes['objectId']
        
        if attributes['eventType'] == 'OBJECT_FINALIZE' and message_id not in cache:
            object_metadata = json.loads(data)
            cache[message_id] = True
            obj_path = object_metadata['name']
            bucket_name = object_metadata['bucket']

            source_blob_name = obj_path
            file_name = source_blob_name.split("/")[-1]
            project = object_metadata["metadata"]["project"]

            cdx = CodeDxAPI.CodeDx(base_url, codedx_api_key)
            
            slack_text = "New vulnerability report detected in GCS bucket: \
                https://console.cloud.google.com/storage/browser/{}/{}".format(bucket_name, obj_path)
            response = webhook.send(text=slack_text)

            # Download file
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(file_name)

            # Upload Zap report to Codedx
            cdx.update_projects()
            if project not in list(cdx.projects):
                cdx.create_project(project)
            res = cdx.analyze(project, file_name)
        
        message.ack()
        
    except Exception as e:
        print('Error uploading reports to CodeDx: {}'.format(e.args))
        slack_text = "Error uploading vulnerability report to Codedx."
        response = webhook.send(text=slack_text)


def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, subscription_name)

    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)

    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull.result()
        except TimeoutError as error:
            streaming_pull.cancel()
            raise error


if __name__ == '__main__':
    main()
