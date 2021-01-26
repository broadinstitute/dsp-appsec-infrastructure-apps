from zap_scans import compliance_scan
import subprocess
import os, signal
from datetime import date
from codedx_api import CodeDxAPI
from slack import WebhookClient

def slack_message(msg):
    slack_url = os.getenv('SLACK_WEBHOOK')
    webhook = WebhookClient(slack_url)            
    response = webhook.send(text=msg)

def get_codedx_client():
    base_url = os.getenv('CODEDX_URL')
    codedx_api_key = os.getenv('CODEDX_API_KEY')
    cdx = CodeDxAPI.CodeDx(base_url, codedx_api_key)

def codedx_upload(project, file_name):
    cdx = get_codedx_client()
    cdx.update_projects()

    if project not in list(cdx.projects):
            cdx.create_project(project)

    cdx.analyze(project, file_name)

def get_codedx_report(project, filters={}):
    cdx = get_codedx_client()
    created_on = date.today().strftime("%Y%m%d%H%M%S")
    if not filters:
        report_title = project + '_report_' + created_on + ".pdf"
    else:
        report_title = project + '_triage_report_' + created_on + ".pdf"
    cdx.get_pdf(project, 
                summary_mode="detailed", 
                details_mode="with-source", 
                include_result_details=True, 
                include_comments=True, 
                include_request_response=False, 
                file_name=report_title,
                filters=filters)
    return report_title

def main():
    # configure logging
    logging.basicConfig(level=logging.INFO)
    
    # get scan variables
    codedx_project = os.getenv('CODEX_PROJECT')
    target_url = os.getenv('URL')
    scan_type = os.getenv('SCAN_TYPE')

    # start the zap proxy
    zap_scanner = subprocess.Popen(["/bin/bash", "start-zap.sh"])
    # need separate process to "wait" until zap has started up
    subprocess.call('./zap-status.sh')

    # run the scan
    filename = compliance_scan(codedx_project, target_url, scan_type)

    # upload to codedx
    codedx_upload(codedx_project, filename)

    # kill the zap proxy
    os.killpg(os.getpgid(zap_scanner.pid), signal.SIGTERM)

if __name__ == "__main__":
    main()