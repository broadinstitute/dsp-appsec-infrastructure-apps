#!/usr/bin/env python
# Pull subscriber

import json
import os
from codedx_api import CodeDxAPI
from google.cloud import pubsub_v1, storage

codedx_api_key = os.environ['codedx_api_key']
project_id = os.environ['PROJECT_ID']
subscription_name = os.environ['SUBSCRIPTION']
base_url = os.environ['CODEDX_URL']

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    project_id, subscription_name)

def callback(message):
    print('Callback started...')
    try:
        data = message.data.decode('utf-8')
        attributes = message.attributes
        message.ack()
        if attributes['eventType'] != 'OBJECT_FINALIZE':
            return
        object_metadata = json.loads(data)
        obj_path = object_metadata['name']
        print('Process file: {}'.format(obj_path))

        bucket_name = object_metadata["bucket"]
        source_blob_name = object_metadata["name"]
        file_name = source_blob_name.split("/")[-1]
        project = object_metadata["metadata"]["project"]

        # Download file
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(file_name)

        # Upload Zap report to Codedx
        cdx = CodeDxAPI.CodeDx(base_url, codedx_api_key)
        cdx.update_projects()
        if project not in list(cdx.projects):
            cdx.create_project(project)
        res = cdx.analyze(project, file_name)
        print(res)

    except Exception as e:
        print('Something wrong happened: {}'.format(e.args))


def main():
    print("SUBSCRIPTION NAME: {}".format(subscription_name))
    print("SUBSCRIPTION PROJECT: {}".format(project_id))
    print("SUBSCRIPTION PATH: {}".format(subscription_path))

    try:
        for element in subscriber.list_subscriptions(project_id):
            print(element)
    except:
        pass
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    streaming_pull.result()

if __name__ == '__main__':
    main()
