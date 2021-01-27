from zap_scans import compliance_scan
import os
from datetime import date
from codedx_api import CodeDxAPI
from slack import WebhookClient
import logging

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

    # run the scan
    filename = compliance_scan(codedx_project, target_url, scan_type)

    # upload to codedx
    codedx_upload(codedx_project, filename)

if __name__ == "__main__":
    main()
