#!/usr/bin/env python3

import logging
import os
from datetime import datetime

from codedx_api import CodeDxAPI
from google.cloud import storage

from notify import slack_message, slack_attach
from zap import compliance_scan


def upload_gcp(bucket_name, scan, filename):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    date = datetime.today().strftime('%Y%m%d')
    path = f'{scan}s/{date}/{filename}'
    blob = bucket.blob(path)
    blob.upload_from_filename(filename)
    location = f"https://console.cloud.google.com/storage/browser/{bucket_name}/{path}"
    return location


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

def codedx_report(project, channel='#automated-security-scans'):
    print(f"Getting PDF report from Codedx project: {project}")
    cdx = get_codedx_client()
    cdx.update_projects()
    if project not in list(cdx.projects):
        print("Error getting PDF report: project does not exist for PDF report.")
        return
    now = datetime.now()
    report_title = f'{project}_report_{now:%Y%m%d}.pdf'
    filters = {
        "status": ["false-positive", "ignored", "mitigated", "fixed"]
    }

    cdx.get_pdf(project,
                summary_mode="detailed",
                details_mode="with-source",
                include_result_details=True,
                include_comments=True,
                include_request_response=False,
                file_name=report_title,
                filters=filters)

    print(f"Uploading PDF report to Slack channel: {channel}")
    slack_attach(channel, report_title)

def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)
    # get scan variables
    codedx_project = os.getenv('CODEDX_PROJECT')
    target_url = os.getenv('URL')
    scan_type = os.getenv('SCAN_TYPE')
    bucket_name = os.getenv('BUCKET_NAME')
    slack_channel = os.getenv('SLACK_CHANNEL')

    # run the scan
    filename = compliance_scan(codedx_project, target_url, '#automated-security-scans', scan_type)
    if bucket_name:
        storage_object_url = upload_gcp(bucket_name, scan_type, filename)
        if scan_type == 'ui-scan':  # right now this is what we have to check for compliance
            slack_text = f"<!here> New vulnerability report uploaded to GCS bucket: {storage_object_url}"
            slack_message('#automated-security-scans', slack_text)
    # upload to codedx
    codedx_upload(codedx_project, filename)
    if slack_channel:
        codedx_report(codedx_project, slack_channel)


if __name__ == "__main__":
    main()
