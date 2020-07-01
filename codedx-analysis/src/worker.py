#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
    streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
    streaming_pull.result()

if __name__ == '__main__':
    main()
