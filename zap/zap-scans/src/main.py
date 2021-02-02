import logging
import os
from zap_scans import compliance_scan
from codedx_api import CodeDxAPI
from slack import WebhookClient
from google.cloud import storage
from datetime import datetime

def upload_gcp(bucket_name, scan, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime('%Y%m%d')
    path = f'{scan}s/{date}/{filename}'
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    location = f"https://console.cloud.google.com/storage/browser/{bucket_name}/{path}"
    return location

def slack_message(msg):
    slack_url = os.getenv('SLACK_WEBHOOK')
    webhook = WebhookClient(slack_url)
    response = webhook.send(text=msg)
    if response.status_code != 200:
        print(f'Response from slack returned an error: {response.body}')

def get_codedx_client():
    base_url = os.getenv('CODEDX_URL')
    codedx_api_key = os.getenv('CODEDX_API_KEY')
    cdx = CodeDxAPI.CodeDx(base_url, codedx_api_key)
    return cdx

def codedx_upload(project, file_name):
    cdx = get_codedx_client()
    cdx.update_projects()

    if project not in list(cdx.projects):
        cdx.create_project(project)

    cdx.analyze(project, file_name)

def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)
    # get scan variables
    codedx_project = os.getenv('CODEX_PROJECT')
    target_url = os.getenv('URL')
    scan_type = os.getenv('SCAN_TYPE')
    bucket_name = os.getenv('BUCKET_NAME')

    # run the scan
    filename = compliance_scan(codedx_project, target_url, scan_type)
    if bucket_name:
        storage_object_url = upload_gcp(bucket_name, scan_type, filename)
        if scan_type == 'ui-scan': # right now this is what we have to check for compliance
            slack_text = f"<!here> New vulnerability report uploaded to GCS bucket: {storage_object_url}"
            slack_message(slack_text)
    # upload to codedx
    codedx_upload(codedx_project, filename)

if __name__ == "__main__":
    main()
